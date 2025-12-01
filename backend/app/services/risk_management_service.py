from app import db
from app.models.risk_management import RiskRegister, FMEA, FailureMode, RiskMitigation
from datetime import datetime

class RiskManagementService:
    @staticmethod
    def create_risk(project_id, description, category, severity, probability, owner_id):
        rpn = severity * probability
        risk = RiskRegister(
            project_id=project_id,
            risk_description=description,
            risk_category=category,
            severity=severity,
            probability=probability,
            rpn=rpn,
            owner_id=owner_id
        )
        db.session.add(risk)
        db.session.commit()
        return risk

    @staticmethod
    def update_risk_mitigation(risk_id, mitigation_strategy, status):
        risk = RiskRegister.query.get(risk_id)
        if risk:
            risk.mitigation_strategy = mitigation_strategy
            risk.status = status
            db.session.commit()
        return risk

    @staticmethod
    def create_fmea(process_id, team_lead_id):
        fmea = FMEA(process_id=process_id, team_lead_id=team_lead_id)
        db.session.add(fmea)
        db.session.commit()
        return fmea

    @staticmethod
    def add_failure_mode(fmea_id, description, severity, occurrence, detection):
        rpn = severity * occurrence * detection
        mode = FailureMode(
            fmea_id=fmea_id,
            failure_description=description,
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            rpn=rpn
        )
        db.session.add(mode)
        db.session.commit()
        return mode

    @staticmethod
    def create_mitigation_action(risk_id, action, target_date, responsible_user_id):
        mitigation = RiskMitigation(
            risk_id=risk_id,
            action_description=action,
            target_date=target_date,
            responsible_user_id=responsible_user_id
        )
        db.session.add(mitigation)
        db.session.commit()
        return mitigation

    @staticmethod
    def get_high_risk_items(project_id, threshold=50):
        return RiskRegister.query.filter(
            RiskRegister.project_id == project_id,
            RiskRegister.rpn >= threshold
        ).all()

    @staticmethod
    def get_fmea_summary(fmea_id):
        fmea = FMEA.query.get(fmea_id)
        failure_modes = FailureMode.query.filter_by(fmea_id=fmea_id).all()
        high_rpn = [m for m in failure_modes if m.rpn >= 100]
        return {'fmea': fmea, 'modes': failure_modes, 'high_risk': high_rpn}
