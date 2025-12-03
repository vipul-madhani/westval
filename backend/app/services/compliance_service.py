from app.models.compliance import ComplianceDocument, RequirementTraceability, ComplianceTrail
from app.utils.audit import log_audit_event
import json

class ComplianceService:
    @staticmethod
    def create_doc(user_id, doc_type, title, content, req_id, db):
        doc=ComplianceDocument(doc_type=doc_type, title=title, content=content, requirement_id=req_id, created_by_id=user_id)
        db.session.add(doc)
        db.session.commit()
        log_audit_event(user_id, 'DOC_CREATED', f'Doc {doc.id} created', db)
        return doc
    
    @staticmethod
    def trace_requirement(user_id, req_id, doc_id, db):
        trace=RequirementTraceability(requirement_id=req_id, doc_id=doc_id)
        db.session.add(trace)
        db.session.commit()
        log_audit_event(user_id, 'TRACE_CREATED', f'Trace {trace.id} created', db)
        return trace
    
    @staticmethod
    def log_change(user_id, doc_id, action, details, db):
        trail=ComplianceTrail(doc_id=doc_id, action=action, changed_by_id=user_id, details=details)
        db.session.add(trail)
        db.session.commit()
        log_audit_event(user_id, 'CHANGE_LOGGED', f'Change {trail.id} logged', db)
        return trail
    
    @staticmethod
    def get_doc_traceability(doc_id, db):
        traces=db.query(RequirementTraceability).filter_by(doc_id=doc_id).all()
        return [{'id': t.id, 'req_id': t.requirement_id, 'status': t.status} for t in traces]
