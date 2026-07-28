from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class WebsitePage(Base):
    __tablename__ = "website_pages"

    id              = Column(Integer, primary_key=True)
    client_id       = Column(Integer, ForeignKey("clients.id"), nullable=False)
    url             = Column(String, nullable=False)
    page_name       = Column(String, default="")
    page_type       = Column(String, default="landing")
    bounce_rate     = Column(Float, default=0.0)
    avg_time        = Column(Float, default=0.0)
    conversions     = Column(Integer, default=0)
    ux_score        = Column(Float, default=0.0)
    issues          = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    client          = relationship("Client", back_populates="website_pages")
    recommendations_list = relationship("WebsiteRecommendation", back_populates="page", cascade="all, delete-orphan")


class WebsiteRecommendation(Base):
    __tablename__ = "website_recommendations"

    id          = Column(Integer, primary_key=True)
    page_id     = Column(Integer, ForeignKey("website_pages.id"), nullable=False)
    category    = Column(String, default="ux")          # ux, content, cro, seo, speed
    priority    = Column(String, default="medium")
    title       = Column(String, default="")
    description = Column(Text, default="")
    before_text = Column(Text, default="")
    after_text  = Column(Text, default="")
    status      = Column(String, default="pending")     # pending, in-progress, done
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    page = relationship("WebsitePage", back_populates="recommendations_list")
