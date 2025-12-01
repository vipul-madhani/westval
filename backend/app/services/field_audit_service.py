from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from app.models import FieldAuditLog, ChangeRequest, DocumentComment, RiskAssessment, User
import hashlib
import json

class FieldAuditService:
    """Service layer for field-level audit trail management."""
    
    @staticmethod
    def log_field_change(entity_type, entity_id, field_name, old_value, new_value, user_id, ip_address=None, change_reason=None):
        """Create an immutable field audit log entry."""
        # Serialize values for storage
        old_val_str = json.dumps(old_value) if not isinstance(old_value, str) else old_value
        new_val_str = json.dumps(new_value) if not isinstance(new_value, str) else new_value
        
        # Get previous hash for chain
        previous_log = FieldAuditLog.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(desc(FieldAuditLog.created_at)).first()
        
        previous_hash = previous_log.change_hash if previous_log else None
        
        # Create new audit log
        audit_log = FieldAuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            old_value=old_val_str,
            new_value=new_val_str,
            user_id=user_id,
            ip_address=ip_address,
            change_reason=change_reason,
            previous_hash=previous_hash
        )
        
        # Calculate hash
        audit_log.change_hash = audit_log.calculate_hash()
        
        db.session.add(audit_log)
        db.session.commit()
        return audit_log
    
    @staticmethod
    def verify_audit_trail(entity_type, entity_id):
        """Verify integrity of entire audit trail for an entity."""
        logs = FieldAuditLog.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(FieldAuditLog.created_at).all()
        
        for i, log in enumerate(logs):
            if not log.verify_integrity():
                return False, f"Integrity check failed at log {i+1}"
            if i > 0 and log.previous_hash != logs[i-1].change_hash:
                return False, f"Chain integrity broken at log {i+1}"
        return True, "All logs verified"
    
    @staticmethod
    def get_audit_history(entity_type, entity_id, limit=50):
        """Retrieve audit history for an entity."""
        return FieldAuditLog.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(desc(FieldAuditLog.created_at)).limit(limit).all()
    
    @staticmethod
    def approve_changes(audit_log_ids, approved_by_user_id, notes=None):
        """Bulk approve pending field changes."""
        logs = FieldAuditLog.query.filter(FieldAuditLog.id.in_(audit_log_ids)).all()
        for log in logs:
            log.approval_status = 'approved'
            log.approved_by = approved_by_user_id
            log.approval_timestamp = datetime.utcnow()
        db.session.commit()
        return logs

class ChangeManagementService:
    """Service for change management workflow."""
    
    @staticmethod
    def create_change_request(title, description, change_type, priority, requested_by, external_change_id=None, external_source=None):
        """Create a new change request."""
        # Generate change number
        last_cr = ChangeRequest.query.order_by(desc(ChangeRequest.id)).first()
        cr_number = f"CR-{datetime.utcnow().year}-{(last_cr.id if last_cr else 0) + 1:05d}"
        
        change_request = ChangeRequest(
            change_number=cr_number,
            title=title,
            description=description,
            change_type=change_type,
            priority=priority,
            status='draft',
            requested_by=requested_by,
            external_change_id=external_change_id,
            external_source=external_source
        )
        
        db.session.add(change_request)
        db.session.commit()
        return change_request
    
    @staticmethod
    def submit_change_request(change_id, impact_assessment=None, implementation_plan=None):
        """Submit change request for approval."""
        cr = ChangeRequest.query.get(change_id)
        if cr:
            cr.status = 'submitted'
            cr.submitted_at = datetime.utcnow()
            if impact_assessment:
                cr.impact_assessment = impact_assessment
            if implementation_plan:
                cr.implementation_plan = implementation_plan
            db.session.commit()
        return cr
    
    @staticmethod
    def get_pending_changes(priority=None, limit=50):
        """Get pending change requests."""
        query = ChangeRequest.query.filter(
            ChangeRequest.status.in_(['draft', 'submitted'])
        )
        if priority:
            query = query.filter_by(priority=priority)
        return query.order_by(desc(ChangeRequest.created_at)).limit(limit).all()

class CollaborationService:
    """Service for document collaboration and comments."""
    
    @staticmethod
    def add_comment(entity_type, entity_id, comment_text, author_id, parent_comment_id=None, mentions=None):
        """Add a new comment or reply."""
        comment = DocumentComment(
            entity_type=entity_type,
            entity_id=entity_id,
            comment_text=comment_text,
            comment_author_id=author_id,
            parent_comment_id=parent_comment_id,
            mentions=mentions or []
        )
        
        db.session.add(comment)
        db.session.commit()
        return comment
    
    @staticmethod
    def resolve_comment(comment_id, resolved_by_user_id, resolution_notes=None):
        """Mark a comment as resolved."""
        comment = DocumentComment.query.get(comment_id)
        if comment:
            comment.is_resolved = True
            comment.resolved_by = resolved_by_user_id
            comment.resolved_at = datetime.utcnow()
            if resolution_notes:
                comment.resolution_notes = resolution_notes
            db.session.commit()
        return comment
    
    @staticmethod
    def get_comment_thread(comment_id):
        """Get all comments in a thread."""
        root_comment = DocumentComment.query.get(comment_id)
        if not root_comment:
            return []
        return FieldAuditService._build_comment_tree(root_comment)

class RiskManagementService:
    """Service for risk assessment and FMEA."""
    
    @staticmethod
    def create_risk_assessment(validation_id, risk_description, risk_category, severity, probability, owner_id, current_controls=None):
        """Create a new risk assessment."""
        # Calculate RPN
        rpn = severity * probability
        
        risk = RiskAssessment(
            validation_id=validation_id,
            risk_description=risk_description,
            risk_category=risk_category,
            severity=severity,
            probability=probability,
            risk_priority_number=rpn,
            current_controls=current_controls or [],
            owner_id=owner_id,
            status='open'
        )
        
        # Generate risk ID
        last_risk = RiskAssessment.query.order_by(desc(RiskAssessment.id)).first()
        risk.risk_id = f"RA-{datetime.utcnow().year}-{(last_risk.id if last_risk else 0) + 1:05d}"
        
        db.session.add(risk)
        db.session.commit()
        return risk
    
    @staticmethod
    def update_risk_mitigation(risk_id, mitigation_actions, residual_risk):
        """Update risk with mitigation actions and residual risk."""
        risk = RiskAssessment.query.get(risk_id)
        if risk:
            risk.mitigation_actions = mitigation_actions
            risk.residual_risk = residual_risk
            if residual_risk < 5:
                risk.status = 'mitigated'
            db.session.commit()
        return risk
    
    @staticmethod
    def get_high_risks(validation_id):
        """Get high-priority risks for a validation."""
        return RiskAssessment.query.filter(
            RiskAssessment.validation_id == validation_id,
            RiskAssessment.risk_priority_number >= 50
        ).order_by(desc(RiskAssessment.risk_priority_number)).all()
