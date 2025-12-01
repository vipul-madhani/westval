from flask import Blueprint,request,jsonify
from app.models.admin_config import User,Role
from app.services.auth_service import verify_jwt,hash_password
from app.extensions import db
from functools import wraps
import hashlib,datetime

bp=Blueprint('users',__name__,url_prefix='/api/admin/users')

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
def list_users():
    try:
        users=User.query.all()
        return jsonify([{'id':u.id,'email':u.email,'name':u.name,'role':u.role,'created_at':u.created_at.isoformat()}for u in users]),200
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('',methods=['POST'])
@admin_only
def create_user():
    data=request.json
    try:
        pwd_hash=hash_password(data.get('password','defaultPass123'))
        user=User(email=data.get('email'),name=data.get('name'),password_hash=pwd_hash,role=data.get('role','USER'))
        db.session.add(user)
        db.session.commit()
        return jsonify({'id':user.id,'email':user.email,'name':user.name,'role':user.role,'created_at':user.created_at.isoformat()}),201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400

@bp.route('/<int:uid>',methods=['GET'])
@admin_only
def get_user(uid):
    try:
        user=User.query.get(uid)
        if not user:
            return jsonify({'error':'Not found'}),404
        return jsonify({'id':user.id,'email':user.email,'name':user.name,'role':user.role,'created_at':user.created_at.isoformat()}),200
    except Exception as e:
        return jsonify({'error':str(e)}),400

@bp.route('/<int:uid>',methods=['PUT'])
@admin_only
def update_user(uid):
    data=request.json
    try:
        user=User.query.get(uid)
        if not user:
            return jsonify({'error':'Not found'}),404
        user.name=data.get('name',user.name)
        user.role=data.get('role',user.role)
        db.session.commit()
        return jsonify({'id':user.id,'email':user.email,'name':user.name,'role':user.role}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400

@bp.route('/<int:uid>',methods=['DELETE'])
@admin_only
def delete_user(uid):
    try:
        user=User.query.get(uid)
        if not user:
            return jsonify({'error':'Not found'}),404
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message':'Deleted'}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400

@bp.route('/<int:uid>/role/<role_name>',methods=['PUT'])
@admin_only
def assign_role(uid,role_name):
    try:
        user=User.query.get(uid)
        if not user:
            return jsonify({'error':'Not found'}),404
        role=Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({'error':'Role not found'}),404
        user.role=role_name
        user.updated_at=datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({'id':user.id,'email':user.email,'role':user.role}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),400
