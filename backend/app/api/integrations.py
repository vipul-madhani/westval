"""External integrations API - Complete implementation"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.jira_service import JiraService
from app.services.azure_devops_service import AzureDevOpsService

integrations_bp = Blueprint('integrations', __name__)

jira_service = JiraService()
azure_service = AzureDevOpsService()

@integrations_bp.route('/status', methods=['GET'])
@jwt_required()
def get_integration_status():
    """Get status of all integrations"""
    return jsonify({
        'jira': {
            'connected': jira_service.is_connected(),
            'configured': jira_service.jira_url is not None
        },
        'azure_devops': {
            'connected': azure_service.is_connected(),
            'configured': azure_service.organization is not None
        }
    }), 200

@integrations_bp.route('/jira/sync', methods=['POST'])
@jwt_required()
def jira_sync():
    """Sync requirements from Jira"""
    data = request.get_json()
    project_key = data.get('project_key')
    
    if not project_key:
        return jsonify({'error': 'project_key is required'}), 400
    
    if not jira_service.is_connected():
        return jsonify({'error': 'Jira is not connected'}), 503
    
    try:
        requirements = jira_service.sync_requirements_from_jira(project_key)
        return jsonify({
            'message': f'Synced {len(requirements)} requirements from Jira',
            'requirements': requirements,
            'count': len(requirements)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/jira/project/<project_key>', methods=['GET'])
@jwt_required()
def get_jira_project(project_key):
    """Get Jira project information"""
    if not jira_service.is_connected():
        return jsonify({'error': 'Jira is not connected'}), 503
    
    project_info = jira_service.get_project_info(project_key)
    
    if not project_info:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify(project_info), 200

@integrations_bp.route('/azure-devops/sync', methods=['POST'])
@jwt_required()
def azure_devops_sync():
    """Sync work items from Azure DevOps"""
    data = request.get_json()
    project_name = data.get('project_name')
    
    if not project_name:
        return jsonify({'error': 'project_name is required'}), 400
    
    if not azure_service.is_connected():
        return jsonify({'error': 'Azure DevOps is not connected'}), 503
    
    try:
        work_items = azure_service.sync_work_items(project_name)
        return jsonify({
            'message': f'Synced {len(work_items)} work items from Azure DevOps',
            'work_items': work_items,
            'count': len(work_items)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500