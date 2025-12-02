from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from . import db

class Report(db.Model):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)
    template = Column(JSON)
    data = Column(JSON)
    created_by_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportSchedule(db.Model):
    __tablename__ = 'report_schedules'
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'))
    frequency = Column(String(50))
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportExecution(db.Model):
    __tablename__ = 'report_executions'
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'))
    status = Column(String(50))
    output_format = Column(String(50))
    file_path = Column(String(500))
    executed_at = Column(DateTime, default=datetime.utcnow)
