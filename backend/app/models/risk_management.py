from app import db
from datetime import datetime

class RiskRegister(db.Model):
    __tablename__ = 'risk_register'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    risk_description = db.Column(db.Text, nullable=False)
    risk_category = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.Integer, nullable=False)  # 1-10
    probability = db.Column(db.Integer, nullable=False)  # 1-10
    rpn = db.Column(db.Integer, nullable=False)  # Risk Priority Number = Severity * Probability
    mitigation_strategy = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class FailureMode(db.Model):
    __tablename__ = 'failure_mode'
    id = db.Column(db.Integer, primary_key=True)
    fmea_id = db.Column(db.Integer, db.ForeignKey('fmea.id'), nullable=False)
    failure_description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Integer, nullable=False)  # 1-10
    occurrence = db.Column(db.Integer, nullable=False)  # 1-10
    detection = db.Column(db.Integer, nullable=False)  # 1-10
    rpn = db.Column(db.Integer, nullable=False)  # Severity * Occurrence * Detection
    recommended_action = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FMEA(db.Model):
    __tablename__ = 'fmea'
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('validation_process.id'), nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    team_lead_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='In Progress')
    failure_modes = db.relationship('FailureMode', backref='fmea', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RiskMitigation(db.Model):
    __tablename__ = 'risk_mitigation'
    id = db.Column(db.Integer, primary_key=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('risk_register.id'), nullable=False)
    action_description = db.Column(db.Text, nullable=False)
    target_date = db.Column(db.DateTime, nullable=False)
    responsible_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
