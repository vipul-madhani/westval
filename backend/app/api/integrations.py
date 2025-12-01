"""External integrations API"""
from flask import Blueprint

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/jira/sync', methods=['POST'])
def jira_sync():
    return {'message': 'Jira sync endpoint'}, 200

@integrations_bp.route('/azure-devops/sync', methods=['POST'])
def azure_devops_sync():
    return {'message': 'Azure DevOps sync endpoint'}, 200