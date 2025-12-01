from flask import Blueprint,request,jsonify
from app.services.admin_config_service import AdminConfigService
from app.services.auth_service import verify_jwt
from functools import wraps

bp=Blueprint('admin',__name__,url_prefix='/api/admin')

def admin_only(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=request.headers.get('Authorization','').split(' ')[1] if 'Authorization' in request.headers else None
        if not token or not verify_jwt(token):
            return jsonify({'error':'Unauthorized'}),401
        user=verify_jwt(token)
        if user.get('role')!='ADMIN':
            return jsonify({'error':'Forbidden'}),403
        return f(*args,**kwargs)
    return decorated

@bp.route('/config',methods=['POST'])
@admin_only
def set_config():
    data=request.json
    try:
        cfg=AdminConfigService.set_config(data.get('key'),data.get('value'),data.get('description',''))
        return jsonify(cfg.to_dict()),201
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('/config/<key>',methods=['GET'])
@admin_only
def get_config(key):
    try:
        cfg=AdminConfigService.get_config(key)
        return jsonify(cfg.to_dict() if cfg else {'error':'Not found'}),200 if cfg else 404
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('/workflow',methods=['POST'])
@admin_only
def create_workflow():
    data=request.json
    try:
        wf=AdminConfigService.create_workflow(data.get('name'),data.get('stages'),data.get('approvers'),data.get('sla_days',5),data.get('parallel',False))
        return jsonify(wf.to_dict()),201
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('/workflow/<name>',methods=['GET'])
@admin_only
def get_workflow(name):
    try:
        wf=AdminConfigService.get_workflow(name)
        return jsonify(wf.to_dict() if wf else {'error':'Not found'}),200 if wf else 404
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('/audit',methods=['POST'])
@admin_only
def log_action():
    data=request.json
    try:
        log=AdminConfigService.log_action(data.get('user_id'),data.get('action'),data.get('resource'),data.get('details',''))
        return jsonify(log.to_dict()),201
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('/audit',methods=['GET'])
@admin_only
def get_audit_logs():
    try:
        resource_type=request.args.get('resource_type')
        limit=int(request.args.get('limit',100))
        logs=AdminConfigService.get_audit_logs(resource_type,limit)
        return jsonify([log.to_dict() for log in logs]),200
    except Exception as e:
        return jsonify({'error':str(e)}),400
