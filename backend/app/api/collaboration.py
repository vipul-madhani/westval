from flask import Blueprint, request, jsonify
from app.services.collaboration_service import CollaborationService
from functools import wraps
import jwt

collab_bp = Blueprint('collaboration', __name__, url_prefix='/api/collaboration')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@collab_bp.route('/comments', methods=['POST'])
@token_required
def add_comment():
    data = request.json
    comment = CollaborationService.add_comment(
        data['user_id'],
        data['document_id'],
        data['content'],
        data.get('parent_comment_id')
    )
    return jsonify({
        'id': comment.id,
        'user_id': comment.user_id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat()
    }), 201

@collab_bp.route('/comments/<int:comment_id>/resolve', methods=['PUT'])
@token_required
def resolve_comment(comment_id):
    data = request.json
    comment = CollaborationService.resolve_comment(comment_id, data['resolved_by_id'])
    return jsonify({'status': 'resolved', 'comment_id': comment_id}), 200

@collab_bp.route('/comments/document/<int:doc_id>', methods=['GET'])
@token_required
def get_comments(doc_id):
    comments = CollaborationService.get_comment_thread(doc_id)
    return jsonify([{'id': c.id, 'content': c.content, 'user_id': c.user_id} for c in comments]), 200

@collab_bp.route('/notifications', methods=['POST'])
@token_required
def send_notification():
    data = request.json
    notif = CollaborationService.send_notification(
        data['user_id'],
        data['notification_type'],
        data['source_id'],
        data['message']
    )
    return jsonify({'notification_id': notif.id}), 201

@collab_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
@token_required
def mark_read(notif_id):
    CollaborationService.mark_notification_read(notif_id)
    return jsonify({'status': 'read'}), 200

@collab_bp.route('/notifications/unread/<int:user_id>', methods=['GET'])
@token_required
def get_unread(user_id):
    notifs = CollaborationService.get_unread_notifications(user_id)
    return jsonify([{'id': n.id, 'message': n.message, 'type': n.notification_type} for n in notifs]), 200
