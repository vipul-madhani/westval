from app.extensions import db
from datetime import datetime

class ComplianceDocument(db.Model):
    __tablename__='compliance_docs'
    id=db.Column(db.Integer,primary_key=True)
    doc_type=db.Column(db.String(50),nullable=False)
    title=db.Column(db.String(255),nullable=False)
    content=db.Column(db.Text,nullable=False)
    requirement_id=db.Column(db.Integer,db.ForeignKey('requirements.id'))
    status=db.Column(db.String(20),default='DRAFT')
    created_by_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

class RequirementTraceability(db.Model):
    __tablename__='req_traceability'
    id=db.Column(db.Integer,primary_key=True)
    requirement_id=db.Column(db.Integer,db.ForeignKey('requirements.id'))
    doc_id=db.Column(db.Integer,db.ForeignKey('compliance_docs.id'))
    test_id=db.Column(db.Integer,nullable=True)
    status=db.Column(db.String(20),default='PENDING')
    traced_at=db.Column(db.DateTime,default=datetime.utcnow)

class ComplianceTrail(db.Model):
    __tablename__='compliance_trails'
    id=db.Column(db.Integer,primary_key=True)
    doc_id=db.Column(db.Integer,db.ForeignKey('compliance_docs.id'))
    action=db.Column(db.String(100))
    changed_by_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    timestamp=db.Column(db.DateTime,default=datetime.utcnow)
    details=db.Column(db.Text)
