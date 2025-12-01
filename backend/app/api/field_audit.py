from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.field_audit_service import FieldAuditService, ChangeManagementService, CollaborationService, RiskManagementService
from app.models import FieldAuditLog, ChangeRequest, DocumentComment, RiskAssessment, db
from functools import wraps

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')

# Field Audit Trail Endpoints
@audit_bp.route('/logs/<entity_type>/<int:entity_id>', methods=['GET'])
@jwt_required()
def get_audit_history(entity_type, entity_id):
    """Retrieve audit history for an entity."""
    limit = request.args.get('limit', 50, type=int)
    logs = FieldAuditService.get_audit_history(entity_type, entity_id, limit)
    return jsonify({
        'success': True,
        'count': len(logs),
        'logs': [{
            'id': log.id,
            'field_name': log.field_name,
            'old_value': log.old_value,
            'new_value': log.new_value,
            'user_id': log.user_id,
            'timestamp': log.change_timestamp.isoformat(),
            'change_reason': log.change_reason,
            'approval_status': log.approval_status
        } for log in logs]
    })

@audit_bp.route('/verify/<entity_type>/<int:entity_id>', methods=['GET'])
@jwt_required()
def verify_audit_trail(entity_type, entity_id):
    """Verify integrity of audit trail."""
    is_valid, message = FieldAuditService.verify_audit_trail(entity_type, entity_id)
    return jsonify({'valid': is_valid, 'message': message})

@audit_bp.route('/approve', methods=['POST'])
@jwt_required()
def approve_changes():
    """Approve pending field changes."""
    user_id = get_jwt_identity()
    data = request.json
    log_ids = data.get('log_ids', [])
    approved_logs = FieldAuditService.approve_changes(log_ids, user_id)
    return jsonify({'success': True, 'approved_count': len(approved_logs)})

# Change Management Endpoints
@audit_bp.route('/changes', methods=['POST'])
@jwt_required()
def create_change_request():
    """Create a new change request."""
    user_id = get_jwt_identity()
    data = request.json
    cr = ChangeManagementService.create_change_request(
        title=data['title'],
        description=data['description'],
        change_type=data['change_type'],
        priority=data['priority'],
        requested_by=user_id,
        external_change_id=data.get('external_change_id'),
        external_source=data.get('external_source')
    )
    return jsonify({
        'success': True,
        'change_id': cr.id,
        'change_number': cr.change_number
    }), 201

@audit_bp.route('/changes/<int:change_id>', methods=['GET'])
@jwt_required()
def get_change_request(change_id):
    """Get a specific change request."""
    cr = ChangeRequest.query.get(change_id)
    if not cr:
        return jsonify({'error': 'Change request not found'}), 404
    return jsonify({
        'id': cr.id,
        'change_number': cr.change_number,
        'title': cr.title,
        'status': cr.status,
        'priority': cr.priority,
        'created_at': cr.created_at.isoformat()
    })

@audit_bp.route('/changes/<int:change_id>/submit', methods=['POST'])
@jwt_required()
def submit_change_request(change_id):
    """Submit change request for approval."""
    data = request.json
    cr = ChangeManagementService.submit_change_request(
        change_id,
        impact_assessment=data.get('impact_assessment'),
        implementation_plan=data.get('implementation_plan')
    )
    return jsonify({'success': True, 'status': cr.status if cr else 'not found'})

@audit_bp.route('/changes/pending', methods=['GET'])
@jwt_required()
def get_pending_changes():
    """Get all pending change requests."""
    priority = request.args.get('priority')
    changes = ChangeManagementService.get_pending_changes(priority)
    return jsonify({
        'success': True,
        'count': len(changes),
        'changes': [{'id': cr.id, 'number': cr.change_number, 'title': cr.title} for cr in changes]
    })

# Collaboration/Comments Endpoints
@audit_bp.route('/comments', methods=['POST'])
@jwt_required()
def add_comment():
    """Add a new comment."""
    user_id = get_jwt_identity()
    data = request.json
    comment = CollaborationService.add_comment(
        entity_type=data['entity_type'],
        entity_id=data['entity_id'],
        comment_text=data['text'],
        author_id=user_id,
        parent_comment_id=data.get('parent_id'),
        mentions=data.get('mentions')
    )
    return jsonify({'success': True, 'comment_id': comment.id}), 201

@audit_bp.route('/comments/<int:comment_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_comment(comment_id):
    """Mark a comment as resolved."""
    user_id = get_jwt_identity()
    data = request.json
    comment = CollaborationService.resolve_comment(
        comment_id,
        user_id,
        data.get('resolution_notes')
    )
    return jsonify({'success': True})

# Risk Management Endpoints
@audit_bp.route('/risks', methods=['POST'])
@jwt_required()
def create_risk():
    """Create a new risk assessment."""
    user_id = get_jwt_identity()
    data = request.json
    risk = RiskManagementService.create_risk_assessment(
        validation_id=data['validation_id'],
        risk_description=data['description'],
        risk_category=data['category'],
        severity=data['severity'],
        probability=data['probability'],
        owner_id=user_id,
        current_controls=data.get('controls')
    )
    return jsonify({
        'success': True,
        'risk_id': risk.id,
        'risk_number': risk.risk_id,
        'rpn': risk.risk_priority_number
    }), 201

@audit_bp.route('/risks/<int:risk_id>/mitigate', methods=['POST'])
@jwt_required()
def update_risk(risk_id):
    """Update risk with mitigation plan."""
    data = request.json
    risk = RiskManagementService.update_risk_mitigation(
        risk_id,
        mitigation_actions=data['mitigation_actions'],
        residual_risk=data['residual_risk']
    )
    return jsonify({'success': True, 'status': risk.status if risk else 'not found'})

@audit_bp.route('/risks/validation/<int:validation_id>/high', methods=['GET'])
@jwt_required()
def get_high_risks(validation_id):
    """Get high-priority risks for validation."""
    risks = RiskManagementService.get_high_risks(validation_id)
    return jsonify({
        'success': True,
        'count': len(risks),
        'risks': [{
            'id': r.id,
            'risk_id': r.risk_id,
            'description': r.risk_description,
            'rpn': r.risk_priority_number,
            'status': r.status
        } for r in risks]
    })
