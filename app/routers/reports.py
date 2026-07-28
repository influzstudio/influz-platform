from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Client, MonthlyReport, AdminUser, SocialPost, Lead, AdCampaign

router = APIRouter(prefix="/clients/{client_id}/reports", tags=["reports"])

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")


def require_admin(request: Request, db: Session):
    uid = request.session.get("admin_id")
    if not uid: return RedirectResponse("/login", status_code=303)
    return db.query(AdminUser).filter(AdminUser.id == uid).first()


@router.get("", response_class=HTMLResponse)
def reports_page(request: Request, client_id: int, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)
    reports = db.query(MonthlyReport).filter(MonthlyReport.client_id == client_id).order_by(MonthlyReport.created_at.desc()).all()
    return templates.TemplateResponse("admin/reports.html", {
        "request": request, "admin": admin, "client": client, "reports": reports,
    })


@router.post("/generate")
def generate_report(request: Request, client_id: int, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)

    month = datetime.now().strftime("%Y-%m")
    total_posts = db.query(SocialPost).filter(SocialPost.client_id == client_id).count()
    total_leads = db.query(Lead).filter(Lead.client_id == client_id).count()

    from app.services.report_service import generate_monthly_report
    result = generate_monthly_report(
        business_name=client.business_name,
        industry=client.industry,
        total_posts=total_posts,
        total_leads=total_leads,
    )
    report = MonthlyReport(
        client_id=client_id,
        report_month=month,
        social_summary=result.get("social_summary", ""),
        ads_summary=result.get("ads_summary", ""),
        seo_summary=result.get("seo_summary", ""),
        overall_summary=result.get("overall_summary", ""),
        next_actions=result.get("next_actions", []),
    )
    db.add(report)
    db.commit()
    return RedirectResponse(f"/clients/{client_id}/reports", status_code=303)
