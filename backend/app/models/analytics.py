from app import db
from datetime import datetime
class Dashboard(db.Model):
    __tablename__='dashboard'
    id=db.Column(db.Integer,primary_key=True)
Sprint 11: Analytics Database Models    name=db.Column(db.String(100))
    layout=db.Column(db.JSON)
    filters=db.Column(db.JSON)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
class Widget(db.Model):
    __tablename__='widget'
    id=db.Column(db.Integer,primary_key=True)
    dashboard_id=db.Column(db.Integer,db.ForeignKey('dashboard.id'))
    widget_type=db.Column(db.String(50))
    position=db.Column(db.Integer)
    config=db.Column(db.JSON)
class Metric(db.Model):
    __tablename__='metric'
    id=db.Column(db.Integer,primary_key=True)
    project_id=db.Column(db.Integer,db.ForeignKey('project.id'))
    metric_name=db.Column(db.String(100))
    metric_value=db.Column(db.Float)
    metric_type=db.Column(db.String(50))
    timestamp=db.Column(db.DateTime,default=datetime.utcnow)
class Report(db.Model):
    __tablename__='report'
    id=db.Column(db.Integer,primary_key=True)
    project_id=db.Column(db.Integer,db.ForeignKey('project.id'))
    report_type=db.Column(db.String(100))
    data=db.Column(db.JSON)
    generated_at=db.Column(db.DateTime,default=datetime.utcnow)
    generated_by=db.Column(db.Integer,db.ForeignKey('user.id'))
