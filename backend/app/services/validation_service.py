"""Validation project management service"""
from datetime import datetime
from app import db
from app.models.validation import ValidationProject, ValidationProtocol
from app.models.audit import AuditLog
import uuid

class ValidationService:
    @staticmethod
    def create_project(data, user):
        """Create new validation project"""
        project = ValidationProject(
            project_number=data.get('project_number', f"VAL-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"),
            title=data['title'],
            description=data.get('description'),
            validation_type=data.get('validation_type'),
            methodology=data.get('methodology', 'Waterfall'),
            gamp_category=data.get('gamp_category'),
            risk_level=data.get('risk_level'),
            risk_score=data.get('risk_score'),
            status='Planning',
            owner_id=data.get('owner_id', user.id),
            department=data.get('department', user.department),
            planned_start_date=data.get('planned_start_date'),
            planned_end_date=data.get('planned_end_date'),
            created_by=user.id
        )
        
        db.session.add(project)
        db.session.flush()
        
        # Create audit log
        audit = AuditLog(
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}",
            action='CREATE',
            entity_type='ValidationProject',
            entity_id=project.id,
            entity_name=project.title,
            change_description=f'Validation project created: {project.project_number}',
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()
        
        return project
    
    @staticmethod
    def update_project(project_id, data, user):
        """Update validation project with audit trail"""
        project = ValidationProject.query.get(project_id)
        if not project:
            return None
        
        # Track changes
        changes = []
        for field, new_value in data.items():
            if hasattr(project, field):
                old_value = getattr(project, field)
                if old_value != new_value:
                    changes.append({
                        'field': field,
                        'old': str(old_value),
                        'new': str(new_value)
                    })
                    setattr(project, field, new_value)
        
        # Create audit logs for each change
        for change in changes:
            audit = AuditLog(
                user_id=user.id,
                user_name=f"{user.first_name} {user.last_name}",
                action='UPDATE',
                entity_type='ValidationProject',
                entity_id=project.id,
                entity_name=project.title,
                field_changed=change['field'],
                old_value=change['old'],
                new_value=change['new'],
                change_description=f"Updated {change['field']} from '{change['old']}' to '{change['new']}'",
                timestamp=datetime.utcnow()
            )
            db.session.add(audit)
        
        db.session.commit()
        return project
    
    @staticmethod
    def get_project_statistics():
        """Get validation project statistics"""
        total = ValidationProject.query.count()
        by_status = db.session.query(
            ValidationProject.status,
            db.func.count(ValidationProject.id)
        ).group_by(ValidationProject.status).all()
        
        by_type = db.session.query(
            ValidationProject.validation_type,
            db.func.count(ValidationProject.id)
        ).group_by(ValidationProject.validation_type).all()
        
        return {
            'total_projects': total,
            'by_status': dict(by_status),
            'by_type': dict(by_type)
        }