"""Document management API"""
from flask import Blueprint

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/', methods=['GET', 'POST'])
def documents():
    """List or create documents"""
    return {'message': 'Documents endpoint'}, 200

@documents_bp.route('/<document_id>', methods=['GET', 'PUT', 'DELETE'])
def document_detail(document_id):
    """Get, update, or delete document"""
    return {'message': f'Document {document_id} endpoint'}, 200

@documents_bp.route('/<document_id>/sign', methods=['POST'])
def sign_document(document_id):
    """Electronically sign a document"""
    return {'message': f'Sign document {document_id}'}, 200