from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class MonthlyReport(Base):
    __tablename__ = "monthly_reports"

    id              = Column(Integer, primary_key=True)
    client_id       = Column(Integer, ForeignKey("clients.id"), nullable=False)
    report_month    = Column(String, nullable=False)        # "2026-07"
    social_summary  = Column(Text, default="")
    ads_summary     = Column(Text, default="")
    seo_summary     = Column(Text, default="")
    website_summary = Column(Text, default="")
    overall_summary = Column(Text, default="")
    kpis            = Column(JSON, default={})
    next_actions    = Column(JSON, default=[])
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="monthly_reports")


class Task(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True)
    client_id   = Column(Integer, ForeignKey("clients.id"), nullable=False)
    module      = Column(String, default="social")          # social, seo, ads, website
    title       = Column(String, nullable=False)
    description = Column(Text, default="")
    priority    = Column(String, default="medium")
    status      = Column(String, default="pending")         # pending, in-progress, done
    due_date    = Column(Date, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="tasks")
