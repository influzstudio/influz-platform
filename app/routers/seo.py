from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import Client, SEOKeyword, SEOPage, SEOReport, AdminUser, Task

router = APIRouter(prefix="/clients/{client_id}/seo", tags=["seo"])

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")


def require_admin(request: Request, db: Session):
    uid = request.session.get("admin_id")
    if not uid: return RedirectResponse("/login", status_code=303)
    return db.query(AdminUser).filter(AdminUser.id == uid).first()


@router.get("", response_class=HTMLResponse)
def seo_page(request: Request, client_id: int, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)
    keywords = db.query(SEOKeyword).filter(SEOKeyword.client_id == client_id).all()
    pages = db.query(SEOPage).filter(SEOPage.client_id == client_id).all()
    return templates.TemplateResponse("admin/seo.html", {
        "request": request, "admin": admin, "client": client,
        "keywords": keywords, "pages": pages,
    })


@router.post("/keywords/generate")
def generate_keywords(
    request: Request, client_id: int,
    seed_keywords: str = Form(""),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)

    from app.services.seo_service import generate_keyword_clusters
    keywords = generate_keyword_clusters(
        business_name=client.business_name,
        industry=client.industry,
        city=client.city,
        seed_keywords=seed_keywords,
    )
    for kw in keywords:
        existing = db.query(SEOKeyword).filter(
            SEOKeyword.client_id == client_id,
            SEOKeyword.keyword == kw["keyword"]
        ).first()
        if not existing:
            db.add(SEOKeyword(
                client_id=client_id,
                keyword=kw["keyword"],
                intent=kw.get("intent", "informational"),
                cluster=kw.get("cluster", ""),
                priority=kw.get("priority", "medium"),
            ))
    db.commit()
    return RedirectResponse(f"/clients/{client_id}/seo", status_code=303)


@router.post("/pages/audit")
def audit_page(
    request: Request, client_id: int,
    url: str = Form(...),
    current_title: str = Form(""),
    current_meta: str = Form(""),
    page_content: str = Form(""),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)

    from app.services.seo_service import audit_page as audit_fn
    result = audit_fn(
        url=url, current_title=current_title,
        current_meta=current_meta, page_content=page_content,
        business_name=client.business_name, industry=client.industry,
    )
    existing = db.query(SEOPage).filter(SEOPage.client_id == client_id, SEOPage.url == url).first()
    if existing:
        existing.suggested_title = result.get("suggested_title", "")
        existing.suggested_meta = result.get("suggested_meta", "")
        existing.suggested_h1 = result.get("suggested_h1", "")
        existing.suggested_schema = result.get("suggested_schema", "")
        existing.issues = result.get("issues", [])
    else:
        db.add(SEOPage(
            client_id=client_id, url=url,
            current_title=current_title, current_meta=current_meta,
            suggested_title=result.get("suggested_title", ""),
            suggested_meta=result.get("suggested_meta", ""),
            suggested_h1=result.get("suggested_h1", ""),
            suggested_schema=result.get("suggested_schema", ""),
            issues=result.get("issues", []),
        ))
    db.commit()
    return RedirectResponse(f"/clients/{client_id}/seo", status_code=303)
