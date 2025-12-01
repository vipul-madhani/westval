from flask import Blueprint,request,jsonify
from app.models.admin_config import Role,RolePermission
from app.services.auth_service import verify_jwt
from app.extensions import db
from functools import wraps
import datetime

bp=Blueprint('roles',__name__,url_prefix='/api/admin/roles')

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

@bp.route('',methods=['GET'])
@admin_only
def list_roles():
    try:
        roles=Role.query.all()
        return jsonify([{'id':r.id,'name':r.name,'permissions':[p.permission for p in r.permissions],'created_at':r.created_at.isoformat()}for r in roles]),200
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('',methods=['POST'])
@admin_only
def create_role():
    data=request.json
    try:
        role=Role(name=data.get('name'),description=data.get('description',''))
        db.session.add(role)
        db.session.flush()
        perms=data.get('permissions',[])
        for perm in perms:
            rp=RolePermission(role_id=role.id,permission=perm)
            db.session.add(rp)
        db.session.commit()
        return jsonify({'id':role.id,'name':role.name,'permissions':perms,'created_at':role.created_at.isoformat()}),201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400

@bp.route('/<int:rid>',methods=['GET'])
@admin_only
def get_role(rid):
    try:
        role=Role.query.get(rid)
        if not role:
            return jsonify({'error':'Not found'}),404
        return jsonify({'id':role.id,'name':role.name,'permissions':[p.permission for p in role.permissions],'created_at':role.created_at.isoformat()}),200
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('/<int:rid>',methods=['PUT'])
@admin_only
def update_role(rid):
    data=request.json
    try:
        role=Role.query.get(rid)
        if not role:
            return jsonify({'error':'Not found'}),404
        role.name=data.get('name',role.name)
        role.description=data.get('description',role.description)
        role.updated_at=datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({'id':role.id,'name':role.name}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400

@bp.route('/<int:rid>',methods=['DELETE'])
@admin_only
def delete_role(rid):
    try:
        role=Role.query.get(rid)
        if not role:
            return jsonify({'error':'Not found'}),404
        db.session.delete(role)
        db.session.commit()
        return jsonify({'message':'Deleted'}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400

@bp.route('/<int:rid>/permissions',methods=['POST'])
@admin_only
def add_permission(rid):
    data=request.json
    try:
        role=Role.query.get(rid)
        if not role:
            return jsonify({'error':'Not found'}),404
        perm=data.get('permission')
        rp=RolePermission(role_id=rid,permission=perm)
        db.session.add(rp)
        db.session.commit()
        return jsonify({'id':rp.id,'permission':perm}),201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400

@bp.route('/<int:rid>/permissions/<perm_id>',methods=['DELETE'])
@admin_only
def remove_permission(rid,perm_id):
    try:
        rp=RolePermission.query.get(perm_id)
        if not rp or rp.role_id!=rid:
            return jsonify({'error':'Not found'}),404
        db.session.delete(rp)
        db.session.commit()
        return jsonify({'message':'Permission removed'}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400
