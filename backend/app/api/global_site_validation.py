from flask import Blueprint, request, jsonify
from functools import wraps
from app.services.global_site_validation_service import GlobalSiteValidationService
from app import db

global_site_bp = Blueprint('global_site', __name__, url_prefix='/api/global-site')

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        return f(*args, **kwargs)
    return decorated_function

@global_site_bp.route('/scopes', methods=['POST'])
@require_auth
def create_scope():
    data = request.get_json()
    try:
        scope = GlobalSiteValidationService.create_validation_scope(
            validation_id=data['validation_id'],
            scope_type=data['scope_type'],
            scope_name=data['scope_name'],
            description=data.get('description', ''),
            parent_scope_id=data.get('parent_scope_id'),
            created_by=data.get('created_by')
        )
        return jsonify({'id': scope.id, 'scope_type': scope.scope_type}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@global_site_bp.route('/scopes/<scope_id>/hierarchy', methods=['GET'])
@require_auth
def get_hierarchy(scope_id):
    try:
        from app.models.global_site_validation import ValidationScope
        scope = ValidationScope.query.get(scope_id)
        if not scope:
            return jsonify({'error': 'Not found'}), 404
        hierarchy = GlobalSiteValidationService.get_scope_hierarchy(scope.validation_id)
        return jsonify(hierarchy), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@global_site_bp.route('/templates', methods=['POST'])
@require_auth
def create_template():
    data = request.get_json()
    try:
        global_template, site_instance = GlobalSiteValidationService.create_test_template_from_global(
            global_scope_id=data['global_scope_id'],
            test_case_id=data['test_case_id'],
            site_scope_id=data['site_scope_id']
        )
        return jsonify({
            'global_template_id': global_template.id,
            'site_instance_id': site_instance.id,
            'sync_status': site_instance.sync_status
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@global_site_bp.route('/templates/<template_id>/customize', methods=['POST'])
@require_auth
def customize(template_id):
    data = request.get_json()
    try:
        instance = GlobalSiteValidationService.customize_test_at_site(
            template_id=template_id,
            site_scope_id=data['site_scope_id'],
            customizations=data['customizations']
        )
        return jsonify({
            'template_id': template_id,
            'sync_status': instance.sync_status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@global_site_bp.route('/scopes/<scope_id>/customizations', methods=['GET'])
@require_auth
def get_customizations(scope_id):
    try:
        status = GlobalSiteValidationService.get_customization_status(scope_id)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@global_site_bp.route('/scopes/<scope_id>/lock', methods=['POST'])
@require_auth
def lock(scope_id):
    try:
        data = request.get_json() or {}
        scope = GlobalSiteValidationService.lock_scope(scope_id, data.get('reason'))
        return jsonify({'scope_id': scope_id, 'is_locked': scope.is_locked}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@global_site_bp.route('/scopes/<scope_id>/history', methods=['GET'])
@require_auth
def get_history(scope_id):
    try:
        history = GlobalSiteValidationService.get_change_history(scope_id)
        return jsonify({'history': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@global_site_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200
