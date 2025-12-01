from app import db
from datetime import datetime
class AdminConfig(db.Model):
    __tablename__='admin_config'
    id=db.Column(db.Integer,primary_key=True)
Admin: Configuration Database Models    config_value=db.Column(db.JSON)
    description=db.Column(db.Text)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,onupdate=datetime.utcnow)
class WorkflowConfig(db.Model):
    __tablename__='workflow_config'
    id=db.Column(db.Integer,primary_key=True)
    workflow_name=db.Column(db.String(100),nullable=False)
    stages=db.Column(db.JSON)
    approvers=db.Column(db.JSON)
    sla_days=db.Column(db.Integer)
    parallel_approval=db.Column(db.Boolean,default=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
class RolePermission(db.Model):
    __tablename__='role_permission'
    id=db.Column(db.Integer,primary_key=True)
    role_id=db.Column(db.Integer,db.ForeignKey('role.id'))
    permission=db.Column(db.String(100))
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
class SystemLog(db.Model):
    __tablename__='system_log'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    action=db.Column(db.String(100))
    resource=db.Column(db.String(100))
    details=db.Column(db.JSON)
    timestamp=db.Column(db.DateTime,default=datetime.utcnow)
