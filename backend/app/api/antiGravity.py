from flask import Blueprint,request,jsonify;from .auth_access_control import require_jwt_token;from ..services.antiGravity_integration_service import AntiGravityIntegrationService;ag_bp=Blueprint('antiGravity',__name__,url_prefix='/api/v1/antiGravity');@ag_bp.route('/sync-validation',methods=['POST'])
@require_jwt_token
def sync_validation():validation_id=request.json.get('validation_id');data=request.json.get('data');result=AntiGravityIntegrationService.sync_validation_to_antiGravity(validation_id,data);return jsonify(result),200 if result['status']=='success' else 500;@ag_bp.route('/validation-status/<antigravity_id>',methods=['GET'])
@require_jwt_token
def get_status(antigravity_id):result=AntiGravityIntegrationService.get_validation_status(antigravity_id);return jsonify(result),200;
