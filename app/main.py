"""
Influz Studio Platform — Agency Marketing OS
"""
import os
import json
import secrets
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.database import get_db, init_db, engine
from app.models import (
    Base, Client, AudienceSegment, Platform,
    SocialPost, SEOKeyword, SEOPage,
    AdCampaign, Lead, WebsitePage, Task, MonthlyReport,
    AdminUser, ClientUser
)

# Init
init_db()

app = FastAPI(title="Influz Studio Platform")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("APP_SECRET_KEY", "influz-secret-2026"))
import os as _os
_os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
templates.env.filters["fromjson"] = json.loads
templates.env.filters["tojson"] = json.dumps


# ── Auth helpers ───────────────────────────────────────────────────────────────
def get_admin(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("admin_id")
    if not user_id:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


def require_admin(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("admin_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    return db.query(AdminUser).filter(AdminUser.id == user_id).first()


# ── Seed admin on startup ──────────────────────────────────────────────────────
@app.on_event("startup")
def seed_admin():
    from sqlalchemy.orm import Session as S
    db = S(engine)
    try:
        if not db.query(AdminUser).first():
            admin = AdminUser(
                email=os.getenv("ADMIN_EMAIL", "admin@influzstudio.com"),
                name="Gaurrav Srivastava",
                password_hash=AdminUser.hash_password(os.getenv("ADMIN_PASSWORD", "influz2026")),
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


# ── Auth routes ────────────────────────────────────────────────────────────────
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


@app.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(AdminUser).filter(AdminUser.email == email).first()
    if user and user.verify_password(password):
        request.session["admin_id"] = user.id
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("admin/login.html", {
        "request": request, "error": "Invalid credentials"
    })


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# ── Admin dashboard ────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse):
        return admin
    clients = db.query(Client).filter(Client.is_active == True).order_by(Client.created_at).all()
    stats = {
        "total_clients": len(clients),
        "total_posts": db.query(SocialPost).count(),
        "total_leads": db.query(Lead).count(),
        "total_tasks": db.query(Task).filter(Task.status == "pending").count(),
    }
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "admin": admin,
        "clients": clients, "stats": stats,
    })


# ── Client CRUD ────────────────────────────────────────────────────────────────
@app.get("/clients/new", response_class=HTMLResponse)
def new_client_form(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    return templates.TemplateResponse("admin/client_form.html", {
        "request": request, "admin": admin, "client": None
    })


@app.post("/clients/new")
def new_client_submit(
    request: Request,
    business_name: str = Form(...),
    industry: str = Form(...),
    website_url: str = Form(""),
    brand_voice: str = Form(...),
    usp: str = Form(""),
    goals: list[str] = Form([]),
    city: str = Form(""),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    slug = business_name.lower().replace(" ", "-").replace("_", "-")
    client = Client(
        slug=slug, business_name=business_name, industry=industry,
        website_url=website_url, brand_voice=brand_voice, usp=usp,
        goals=goals, city=city,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return RedirectResponse(f"/clients/{client.id}", status_code=303)


@app.get("/clients/{client_id}", response_class=HTMLResponse)
def client_overview(request: Request, client_id: int, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    recent_posts = db.query(SocialPost).filter(SocialPost.client_id == client_id).order_by(SocialPost.post_date.desc()).limit(5).all()
    pending_tasks = db.query(Task).filter(Task.client_id == client_id, Task.status == "pending").limit(5).all()
    recent_leads = db.query(Lead).filter(Lead.client_id == client_id).order_by(Lead.created_at.desc()).limit(5).all()
    platforms = db.query(Platform).filter(Platform.client_id == client_id).all()
    return templates.TemplateResponse("admin/client_overview.html", {
        "request": request, "admin": admin, "client": client,
        "recent_posts": recent_posts, "pending_tasks": pending_tasks,
        "recent_leads": recent_leads, "platforms": platforms,
        "today": date.today().isoformat(),
    })


# Include module routers
from app.routers import social, seo, ads, website, reports
app.include_router(social.router)
app.include_router(seo.router)
app.include_router(ads.router)
app.include_router(website.router)
app.include_router(reports.router)
