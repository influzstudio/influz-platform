from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, WebsitePage, WebsiteRecommendation, AdminUser

router = APIRouter(prefix="/clients/{client_id}/website", tags=["website"])

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")


def require_admin(request: Request, db: Session):
    uid = request.session.get("admin_id")
    if not uid: return RedirectResponse("/login", status_code=303)
    return db.query(AdminUser).filter(AdminUser.id == uid).first()


@router.get("", response_class=HTMLResponse)
def website_page(request: Request, client_id: int, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)
    pages = db.query(WebsitePage).filter(WebsitePage.client_id == client_id).all()
    return templates.TemplateResponse("admin/website.html", {
        "request": request, "admin": admin, "client": client, "pages": pages,
    })


@router.post("/audit")
def audit_website(
    request: Request, client_id: int,
    url: str = Form(...),
    page_content: str = Form(""),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)

    from app.services.website_service import audit_page
    result = audit_page(url=url, content=page_content,
                        business_name=client.business_name, industry=client.industry)
    page = WebsitePage(
        client_id=client_id, url=url,
        issues=result.get("issues", []),
        ux_score=result.get("ux_score", 0.0),
        recommendations=result.get("recommendations", []),
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    for rec in result.get("detailed_recommendations", []):
        db.add(WebsiteRecommendation(
            page_id=page.id,
            category=rec.get("category", "ux"),
            priority=rec.get("priority", "medium"),
            title=rec.get("title", ""),
            description=rec.get("description", ""),
            before_text=rec.get("before", ""),
            after_text=rec.get("after", ""),
        ))
    db.commit()
    return RedirectResponse(f"/clients/{client_id}/website", status_code=303)
