from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import json
from datetime import date

from app.database import get_db
from app.models import Client, AdCampaign, AdAsset, Lead, AdminUser

router = APIRouter(prefix="/clients/{client_id}/ads", tags=["ads"])

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")


def require_admin(request: Request, db: Session):
    uid = request.session.get("admin_id")
    if not uid: return RedirectResponse("/login", status_code=303)
    return db.query(AdminUser).filter(AdminUser.id == uid).first()


@router.get("", response_class=HTMLResponse)
def ads_page(request: Request, client_id: int, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)
    campaigns = db.query(AdCampaign).filter(AdCampaign.client_id == client_id).all()
    leads = db.query(Lead).filter(Lead.client_id == client_id).order_by(Lead.created_at.desc()).limit(20).all()
    return templates.TemplateResponse("admin/ads.html", {
        "request": request, "admin": admin, "client": client,
        "campaigns": campaigns, "leads": leads,
    })


@router.post("/campaigns/generate")
def generate_campaign(
    request: Request, client_id: int,
    campaign_type: str = Form("leads"),
    platform: str = Form("meta"),
    objective: str = Form(""),
    budget_daily: float = Form(500.0),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    if isinstance(admin, RedirectResponse): return admin
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(404)

    from app.services.ads_service import generate_ad_assets
    result = generate_ad_assets(
        business_name=client.business_name,
        industry=client.industry,
        campaign_type=campaign_type,
        platform=platform,
        objective=objective or client.usp,
        brand_voice=client.brand_voice,
    )
    campaign = AdCampaign(
        client_id=client_id,
        platform=platform,
        campaign_type=campaign_type,
        name=f"{client.business_name} — {campaign_type.title()} — {platform.title()}",
        objective=objective,
        budget_daily=budget_daily,
        status="draft",
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    for asset in result.get("assets", []):
        db.add(AdAsset(
            campaign_id=campaign.id,
            headline=asset.get("headline", ""),
            description=asset.get("description", ""),
            cta=asset.get("cta", ""),
            creative_brief=asset.get("creative_brief", ""),
            asset_type="copy",
        ))
    db.commit()
    return RedirectResponse(f"/clients/{client_id}/ads", status_code=303)
