"""Document management service with version control"""
from datetime import datetime
from app import db
from app.models.document import Document, DocumentTemplate, ElectronicSignature
from app.models.audit import AuditLog
import hashlib
import uuid

class DocumentService:
    @staticmethod
    def create_document(data, user, file_content=None):
        """Create new document with version control"""
        document = Document(
            document_number=data.get('document_number', f"DOC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"),
            title=data['title'],
            document_type=data.get('document_type'),
            version='1.0',
            is_current_version=True,
            description=data.get('description'),
            content=data.get('content'),
            status='Draft',
            category=data.get('category'),
            tags=data.get('tags', []),
            owner_id=user.id,
            department=data.get('department', user.department),
            is_gxp=data.get('is_gxp', True),
            regulatory_references=data.get('regulatory_references', [])
        )
        
        db.session.add(document)
        db.session.flush()
        
        # Create audit log
        audit = AuditLog(
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}",
            action='CREATE',
            entity_type='Document',
            entity_id=document.id,
            entity_name=document.title,
            change_description=f'Document created: {document.document_number}',
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()
        
        return document
    
    @staticmethod
    def create_new_version(document_id, data, user):
        """Create new version of existing document"""
        original = Document.query.get(document_id)
        if not original:
            return None
        
        # Mark original as not current
        original.is_current_version = False
        
        # Parse version and increment
        major, minor = map(int, original.version.split('.'))
        if data.get('major_version'):
            major += 1
            minor = 0
        else:
            minor += 1
        
        # Create new version
        new_document = Document(
            document_number=original.document_number,
            title=data.get('title', original.title),
            document_type=original.document_type,
            version=f"{major}.{minor}",
            is_current_version=True,
            parent_document_id=original.id,
            description=data.get('description', original.description),
            content=data.get('content', original.content),
            status='Draft',
            category=original.category,
            tags=data.get('tags', original.tags),
            owner_id=user.id,
            department=original.department,
            is_gxp=original.is_gxp,
            regulatory_references=original.regulatory_references
        )
        
        db.session.add(new_document)
        db.session.flush()
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}",
            action='VERSION_CREATE',
            entity_type='Document',
            entity_id=new_document.id,
            entity_name=new_document.title,
            change_description=f'New version {new_document.version} created from {original.version}',
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()
        
        return new_document
    
    @staticmethod
    def sign_document(document_id, user, signature_data, ip_address=None):
        """Create electronic signature for document (21 CFR Part 11)"""
        document = Document.query.get(document_id)
        if not document:
            return None
        
        # Create signature hash
        signature_string = f"{user.id}{document.id}{datetime.utcnow().isoformat()}{signature_data.get('reason', '')}"
        signature_hash = hashlib.sha256(signature_string.encode()).hexdigest()
        
        signature = ElectronicSignature(
            user_id=user.id,
            signer_name=f"{user.first_name} {user.last_name}",
            signer_role=signature_data.get('role', user.job_title),
            signature_meaning=signature_data.get('meaning', 'Reviewed and Approved'),
            signature_type=signature_data.get('type', 'Approver'),
            reason=signature_data.get('reason'),
            document_id=document.id,
            entity_type='Document',
            entity_id=document.id,
            signature_hash=signature_hash,
            ip_address=ip_address,
            device_info=signature_data.get('device_info'),
            signed_at=datetime.utcnow()
        )
        
        db.session.add(signature)
        
        # Update document status if approved
        if signature_data.get('type') == 'Approver':
            document.status = 'Approved'
            document.approved_at = datetime.utcnow()
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}",
            action='SIGN',
            entity_type='Document',
            entity_id=document.id,
            entity_name=document.title,
            change_description=f'Document electronically signed: {signature.signature_meaning}',
            reason=signature_data.get('reason'),
            timestamp=datetime.utcnow(),
            ip_address=ip_address
        )
        db.session.add(audit)
        db.session.commit()
        
        return signature