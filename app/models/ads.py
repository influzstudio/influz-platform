from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id              = Column(Integer, primary_key=True)
    client_id       = Column(Integer, ForeignKey("clients.id"), nullable=False)
    platform        = Column(String, default="meta")       # meta, google
    campaign_type   = Column(String, default="leads")      # leads, awareness, retargeting, sales
    name            = Column(String, nullable=False)
    objective       = Column(String, default="")
    budget_daily    = Column(Float, default=0.0)
    budget_total    = Column(Float, default=0.0)
    start_date      = Column(Date, nullable=True)
    end_date        = Column(Date, nullable=True)
    target_audience = Column(JSON, default={})
    platform_campaign_id = Column(String, default="")
    status          = Column(String, default="draft")      # draft, active, paused, completed
    spend           = Column(Float, default=0.0)
    impressions     = Column(Integer, default=0)
    clicks          = Column(Integer, default=0)
    conversions     = Column(Integer, default=0)
    ctr             = Column(Float, default=0.0)
    cpc             = Column(Float, default=0.0)
    cpl             = Column(Float, default=0.0)
    roas            = Column(Float, default=0.0)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    client  = relationship("Client", back_populates="ad_campaigns")
    assets  = relationship("AdAsset", back_populates="campaign", cascade="all, delete-orphan")


class AdAsset(Base):
    __tablename__ = "ad_assets"

    id              = Column(Integer, primary_key=True)
    campaign_id     = Column(Integer, ForeignKey("ad_campaigns.id"), nullable=False)
    asset_type      = Column(String, default="copy")       # copy, creative_brief, image, video
    headline        = Column(String, default="")
    description     = Column(Text, default="")
    cta             = Column(String, default="")
    creative_brief  = Column(Text, default="")
    image_path      = Column(String, default="")
    status          = Column(String, default="draft")
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("AdCampaign", back_populates="assets")


class Lead(Base):
    __tablename__ = "leads"

    id              = Column(Integer, primary_key=True)
    client_id       = Column(Integer, ForeignKey("clients.id"), nullable=False)
    source          = Column(String, default="")           # meta_ad, google_ad, organic, social, direct
    campaign_id     = Column(Integer, ForeignKey("ad_campaigns.id"), nullable=True)
    name            = Column(String, default="")
    email           = Column(String, default="")
    phone           = Column(String, default="")
    message         = Column(Text, default="")
    interest        = Column(String, default="")           # which package/product
    lead_data       = Column(JSON, default={})             # form fields
    score           = Column(Float, default=0.0)           # ML score 0-1
    priority        = Column(String, default="medium")     # high, medium, low
    status          = Column(String, default="new")        # new, contacted, qualified, converted, lost
    converted_at    = Column(DateTime(timezone=True), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    client   = relationship("Client", back_populates="leads")
    campaign = relationship("AdCampaign", foreign_keys=[campaign_id])


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id          = Column(Integer, primary_key=True)
    lead_id     = Column(Integer, ForeignKey("leads.id"), nullable=False)
    score       = Column(Float, default=0.0)
    factors     = Column(JSON, default={})
    model_version = Column(String, default="v1")
    scored_at   = Column(DateTime(timezone=True), server_default=func.now())
