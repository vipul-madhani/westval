"""Workflow management API"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.workflow import WorkflowTask, Notification
from app.services.workflow_service import WorkflowService

workflow_bp = Blueprint('workflow', __name__)

@workflow_bp.route('/tasks/my-tasks', methods=['GET'])
@jwt_required()
def get_my_tasks():
    """Get tasks assigned to current user"""
    user_id = get_jwt_identity()
    status = request.args.get('status')  # PENDING, COMPLETED
    
    tasks = WorkflowService.get_user_tasks(user_id, status)
    
    return jsonify({
        'tasks': [{
            'id': t.id,
            'stage_name': t.stage_name,
            'task_type': t.task_type,
            'status': t.status,
            'entity_type': t.workflow.entity_type,
            'entity_id': t.workflow.entity_id,
            'due_date': t.due_date.isoformat() if t.due_date else None,
            'is_overdue': t.is_overdue,
            'created_at': t.created_at.isoformat(),
            'comments': t.comments
        } for t in tasks]
    }), 200

@workflow_bp.route('/tasks/<task_id>/complete', methods=['POST'])
@jwt_required()
def complete_task(task_id):
    """Complete a workflow task"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    action = data.get('action')  # APPROVED, REJECTED
    comments = data.get('comments')
    
    if not action:
        return jsonify({'error': 'Action is required'}), 400
    
    try:
        task = WorkflowService.complete_task(task_id, user, action, comments)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'message': f'Task {action.lower()} successfully',
            'task': {
                'id': task.id,
                'status': task.status,
                'action_taken': task.action_taken,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/workflow/status', methods=['GET'])
@jwt_required()
def get_workflow_status():
    """Get workflow status for an entity"""
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id')
    
    if not entity_type or not entity_id:
        return jsonify({'error': 'entity_type and entity_id are required'}), 400
    
    status = WorkflowService.get_workflow_status(entity_type, entity_id)
    
    if not status:
        return jsonify({'message': 'No workflow found'}), 404
    
    return jsonify(status), 200

@workflow_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications"""
    user_id = get_jwt_identity()
    
    notifications = Notification.query.filter_by(
        user_id=user_id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'entity_type': n.entity_type,
            'entity_id': n.entity_id,
            'is_read': n.is_read,
            'priority': n.priority,
            'created_at': n.created_at.isoformat()
        } for n in notifications],
        'unread_count': len([n for n in notifications if not n.is_read])
    }), 200

@workflow_bp.route('/notifications/<notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=user_id
    ).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200

@workflow_bp.route('/start-workflow', methods=['POST'])
@jwt_required()
def start_workflow():
    """Start a workflow for an entity"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    
    if not entity_type or not entity_id:
        return jsonify({'error': 'entity_type and entity_id are required'}), 400
    
    try:
        workflow = WorkflowService.start_workflow(entity_type, entity_id, user)
        
        if not workflow:
            return jsonify({'error': 'No workflow definition found'}), 404
        
        return jsonify({
            'message': 'Workflow started successfully',
            'workflow_id': workflow.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500