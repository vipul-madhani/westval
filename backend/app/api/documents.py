"""Document management API - Complete implementation"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.document import Document, DocumentTemplate
from app.services.document_service import DocumentService

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/', methods=['GET'])
@jwt_required()
def list_documents():
    """List documents with filtering"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    doc_type = request.args.get('type')
    status = request.args.get('status')
    
    query = Document.query.filter_by(is_current_version=True)
    
    if doc_type:
        query = query.filter_by(document_type=doc_type)
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Document.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'documents': [{
            'id': d.id,
            'document_number': d.document_number,
            'title': d.title,
            'document_type': d.document_type,
            'version': d.version,
            'status': d.status,
            'category': d.category,
            'created_at': d.created_at.isoformat(),
            'updated_at': d.updated_at.isoformat() if d.updated_at else None
        } for d in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages
    }), 200

@documents_bp.route('/', methods=['POST'])
@jwt_required()
def create_document():
    """Create new document"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        document = DocumentService.create_document(data, user)
        return jsonify({
            'message': 'Document created successfully',
            'document': {
                'id': document.id,
                'document_number': document.document_number,
                'title': document.title,
                'version': document.version,
                'status': document.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get document details"""
    document = Document.query.get(document_id)
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify({
        'id': document.id,
        'document_number': document.document_number,
        'title': document.title,
        'document_type': document.document_type,
        'version': document.version,
        'is_current_version': document.is_current_version,
        'description': document.description,
        'content': document.content,
        'status': document.status,
        'category': document.category,
        'tags': document.tags,
        'is_gxp': document.is_gxp,
        'regulatory_references': document.regulatory_references,
        'created_at': document.created_at.isoformat(),
        'approved_at': document.approved_at.isoformat() if document.approved_at else None,
        'signatures': [{
            'signer_name': s.signer_name,
            'signature_meaning': s.signature_meaning,
            'signed_at': s.signed_at.isoformat()
        } for s in document.signatures]
    }), 200

@documents_bp.route('/<document_id>', methods=['PUT'])
@jwt_required()
def update_document(document_id):
    """Update document"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Update fields
    for field in ['title', 'description', 'content', 'category', 'tags']:
        if field in data:
            setattr(document, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({'message': 'Document updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>/sign', methods=['POST'])
@jwt_required()
def sign_document(document_id):
    """Electronically sign a document (21 CFR Part 11)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    if not data.get('reason'):
        return jsonify({'error': 'Reason for signature is required'}), 400
    
    ip_address = request.remote_addr
    
    try:
        signature = DocumentService.sign_document(
            document_id, user, data, ip_address
        )
        
        if not signature:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'message': 'Document signed successfully',
            'signature': {
                'id': signature.id,
                'signer_name': signature.signer_name,
                'signature_meaning': signature.signature_meaning,
                'signed_at': signature.signed_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>/versions', methods=['POST'])
@jwt_required()
def create_version(document_id):
    """Create new version of document"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    try:
        new_document = DocumentService.create_new_version(document_id, data, user)
        
        if not new_document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'message': 'New version created successfully',
            'document': {
                'id': new_document.id,
                'version': new_document.version,
                'status': new_document.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/templates', methods=['GET'])
@jwt_required()
def list_templates():
    """List document templates"""
    templates = DocumentTemplate.query.filter_by(is_active=True).all()
    
    return jsonify({
        'templates': [{
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'template_type': t.template_type,
            'is_default': t.is_default,
            'version': t.version
        } for t in templates]
    }), 200