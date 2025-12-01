from app.models.global_site_validation import (
    ValidationScope, TestTemplate, TestSiteInstance, 
    RequirementMapping, ScopeChangeLog
)
from app.models.test_management import TestCase
from app import db
from datetime import datetime
from uuid import uuid4
import json

class GlobalSiteValidationService:
    
    @staticmethod
    def create_validation_scope(validation_id, scope_type, scope_name, description, parent_scope_id=None, created_by=None):
        """Create new validation scope (GLOBAL or SITE)"""
        scope = ValidationScope(
            id=str(uuid4()),
            validation_id=validation_id,
            scope_type=scope_type,
            scope_name=scope_name,
            description=description,
            parent_scope_id=parent_scope_id,
            created_by=created_by
        )
        db.session.add(scope)
        db.session.commit()
        return scope
    
    @staticmethod
    def create_test_template_from_global(global_scope_id, test_case_id, site_scope_id, customizations=None):
        """Create global template and deploy to sites"""
        # Create global template
        global_template = TestTemplate(
            id=str(uuid4()),
            scope_id=global_scope_id,
            test_case_id=test_case_id,
            is_global_template=True,
            name=TestCase.query.get(test_case_id).name,
            description=TestCase.query.get(test_case_id).description
        )
        db.session.add(global_template)
        db.session.flush()
        
        # Automatically create site instance
        site_instance = TestSiteInstance(
            id=str(uuid4()),
            template_id=global_template.id,
            site_scope_id=site_scope_id,
            test_case_id=test_case_id,
            name=global_template.name,
            description=global_template.description,
            is_inherited=True,
            sync_status='SYNCED'
        )
        db.session.add(site_instance)
        db.session.commit()
        
        # Log change
        GlobalSiteValidationService._log_scope_change(
            site_scope_id, 'INHERIT', 'TEST', test_case_id, 
            None, {'synced_from_global': global_template.id}
        )
        
        return global_template, site_instance
    
    @staticmethod
    def customize_test_at_site(template_id, site_scope_id, customizations):
        """Apply site-specific customizations to inherited test"""
        site_instance = TestSiteInstance.query.filter_by(
            template_id=template_id,
            site_scope_id=site_scope_id
        ).first()
        
        if site_instance:
            site_instance.customizations = customizations
            site_instance.sync_status = 'CUSTOM'
            db.session.commit()
            
            # Log customization
            GlobalSiteValidationService._log_scope_change(
                site_scope_id, 'CUSTOMIZE', 'TEST', template_id,
                None, customizations
            )
        
        return site_instance
    
    @staticmethod
    def sync_global_to_sites(global_scope_id):
        """Sync global template changes to all site instances"""
        global_templates = TestTemplate.query.filter_by(
            scope_id=global_scope_id,
            is_global_template=True
        ).all()
        
        synced_count = 0
        for template in global_templates:
            site_instances = TestSiteInstance.query.filter_by(
                template_id=template.id
            ).all()
            
            for instance in site_instances:
                if instance.sync_status == 'SYNCED':
                    # Update instance with latest from global
                    instance.updated_at = datetime.utcnow()
                    synced_count += 1
        
        db.session.commit()
        return synced_count
    
    @staticmethod
    def create_requirement_mapping(scope_id, global_requirement_id, site_requirement_id=None, is_customized=False):
        """Map requirements across global and site scopes"""
        mapping = RequirementMapping(
            id=str(uuid4()),
            scope_id=scope_id,
            global_requirement_id=global_requirement_id,
            site_requirement_id=site_requirement_id,
            is_customized=is_customized
        )
        db.session.add(mapping)
        db.session.commit()
        return mapping
    
    @staticmethod
    def get_scope_hierarchy(validation_id):
        """Get complete scope hierarchy for validation"""
        scopes = ValidationScope.query.filter_by(validation_id=validation_id).all()
        
        hierarchy = {
            'global': [],
            'sites': []
        }
        
        for scope in scopes:
            if scope.scope_type == 'GLOBAL':
                hierarchy['global'].append({
                    'id': scope.id,
                    'name': scope.scope_name,
                    'templates': len(scope.test_templates),
                    'is_locked': scope.is_locked
                })
            else:
                hierarchy['sites'].append({
                    'id': scope.id,
                    'name': scope.scope_name,
                    'parent_id': scope.parent_scope_id,
                    'instances': len(scope.templates)
                })
        
        return hierarchy
    
    @staticmethod
    def get_customization_status(site_scope_id):
        """Get detailed customization status for a site"""
        site_instances = TestSiteInstance.query.filter_by(
            site_scope_id=site_scope_id
        ).all()
        
        status = {
            'total': len(site_instances),
            'synced': len([i for i in site_instances if i.sync_status == 'SYNCED']),
            'customized': len([i for i in site_instances if i.sync_status == 'CUSTOM']),
            'out_of_sync': len([i for i in site_instances if i.sync_status == 'OUT_OF_SYNC']),
            'details': []
        }
        
        for instance in site_instances:
            status['details'].append({
                'template_id': instance.template_id,
                'status': instance.sync_status,
                'customizations': instance.customizations
            })
        
        return status
    
    @staticmethod
    def lock_scope(scope_id, reason=None):
        """Lock scope to prevent further changes (for published validations)"""
        scope = ValidationScope.query.get(scope_id)
        if scope:
            scope.is_locked = True
            db.session.commit()
            
            GlobalSiteValidationService._log_scope_change(
                scope_id, 'LOCK', 'SCOPE', scope_id,
                {'is_locked': False}, {'is_locked': True},
                reason
            )
        
        return scope
    
    @staticmethod
    def unlock_scope(scope_id, reason=None):
        """Unlock scope to allow modifications"""
        scope = ValidationScope.query.get(scope_id)
        if scope:
            scope.is_locked = False
            db.session.commit()
            
            GlobalSiteValidationService._log_scope_change(
                scope_id, 'UNLOCK', 'SCOPE', scope_id,
                {'is_locked': True}, {'is_locked': False},
                reason
            )
        
        return scope
    
    @staticmethod
    def get_change_history(scope_id):
        """Get complete audit trail for scope"""
        changes = ScopeChangeLog.query.filter_by(scope_id=scope_id).order_by(
            ScopeChangeLog.changed_at.desc()
        ).all()
        
        history = []
        for change in changes:
            history.append({
                'change_type': change.change_type,
                'entity_type': change.entity_type,
                'entity_id': change.entity_id,
                'old_value': change.old_value,
                'new_value': change.new_value,
                'reason': change.change_reason,
                'changed_by': change.changed_by,
                'changed_at': change.changed_at.isoformat()
            })
        
        return history
    
    @staticmethod
    def _log_scope_change(scope_id, change_type, entity_type, entity_id, old_value=None, new_value=None, reason=None, changed_by=None):
        """Internal method to log scope changes"""
        log_entry = ScopeChangeLog(
            id=str(uuid4()),
            scope_id=scope_id,
            change_type=change_type,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            change_reason=reason,
            changed_by=changed_by
        )
        db.session.add(log_entry)
        db.session.commit()
    
    @staticmethod
    def get_inheritance_status(global_scope_id, site_scope_id):
        """Get inheritance relationship status between global and site"""
        global_templates = TestTemplate.query.filter_by(
            scope_id=global_scope_id,
            is_global_template=True
        ).count()
        
        site_instances = TestSiteInstance.query.filter_by(
            site_scope_id=site_scope_id
        ).count()
        
        synced = TestSiteInstance.query.filter_by(
            site_scope_id=site_scope_id,
            sync_status='SYNCED'
        ).count()
        
        return {
            'global_templates': global_templates,
            'site_instances': site_instances,
            'synced_instances': synced,
            'customized_instances': site_instances - synced,
            'inheritance_percentage': round((synced / site_instances * 100), 2) if site_instances > 0 else 0
        }
