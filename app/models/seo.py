from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class SEOKeyword(Base):
    __tablename__ = "seo_keywords"

    id              = Column(Integer, primary_key=True)
    client_id       = Column(Integer, ForeignKey("clients.id"), nullable=False)
    keyword         = Column(String, nullable=False)
    intent          = Column(String, default="informational")  # informational, transactional, navigational
    cluster         = Column(String, default="")               # topic cluster
    search_volume   = Column(Integer, default=0)
    difficulty      = Column(Float, default=0.0)
    current_rank    = Column(Integer, nullable=True)
    target_rank     = Column(Integer, default=1)
    assigned_url    = Column(String, default="")
    priority        = Column(String, default="medium")         # high, medium, low
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="seo_keywords")


class SEOPage(Base):
    __tablename__ = "seo_pages"

    id                  = Column(Integer, primary_key=True)
    client_id           = Column(Integer, ForeignKey("clients.id"), nullable=False)
    url                 = Column(String, nullable=False)
    page_type           = Column(String, default="landing")     # landing, blog, product, home
    current_title       = Column(String, default="")
    current_meta        = Column(Text, default="")
    suggested_title     = Column(String, default="")
    suggested_meta      = Column(Text, default="")
    suggested_h1        = Column(String, default="")
    suggested_schema    = Column(Text, default="")
    internal_links      = Column(JSON, default=[])
    issues              = Column(JSON, default=[])
    score               = Column(Float, default=0.0)
    status              = Column(String, default="pending")     # pending, optimized, published
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="seo_pages")


class SEOReport(Base):
    __tablename__ = "seo_reports"

    id              = Column(Integer, primary_key=True)
    client_id       = Column(Integer, ForeignKey("clients.id"), nullable=False)
    report_date     = Column(DateTime(timezone=True), server_default=func.now())
    organic_traffic = Column(Integer, default=0)
    keywords_top10  = Column(Integer, default=0)
    keywords_top3   = Column(Integer, default=0)
    backlinks       = Column(Integer, default=0)
    domain_rating   = Column(Float, default=0.0)
    top_pages       = Column(JSON, default=[])
    opportunities   = Column(JSON, default=[])
    summary         = Column(Text, default="")              # AI-generated summary
