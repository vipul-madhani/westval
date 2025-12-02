from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
from ..models.encryption_backup import DataEncryption, BackupRecord, EncryptionAlgorithm, BackupStatus
from ..services.encryption_backup_service import EncryptionBackupService
from ..models.auth import User
from ..models.audit import AuditLog
from sqlalchemy import db
import jwt
import os

encryption_bp = Blueprint('encryption', __name__, url_prefix='/api/encryption')
backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Missing auth token'}), 401
        try:
            data = jwt.decode(token.split(' ')[1], SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

@encryption_bp.route('/encrypt', methods=['POST'])
@token_required
def encrypt_data(current_user_id):
    try:
        data = request.get_json()
        plaintext = data.get('plaintext')
        key_id = data.get('key_id')
        
        if not plaintext or not key_id:
            return jsonify({'error': 'Missing plaintext or key_id'}), 400
        
        ciphertext, nonce, tag = EncryptionBackupService.encrypt_data(plaintext, key_id)
        
        enc_record = DataEncryption(
            plaintext_hash=EncryptionBackupService.hash_data(plaintext),
            ciphertext=ciphertext,
            nonce=nonce,
            tag=tag,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id=key_id,
            created_by_id=current_user_id
        )
        db.session.add(enc_record)
        db.session.commit()
        
        audit_log = AuditLog(
            action='ENCRYPT_DATA',
            entity_type='DataEncryption',
            entity_id=enc_record.id,
            user_id=current_user_id,
            details=f'Encrypted data with key {key_id}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'encryption_id': enc_record.id, 'ciphertext': ciphertext}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@encryption_bp.route('/decrypt/<int:encryption_id>', methods=['POST'])
@token_required
def decrypt_data(current_user_id, encryption_id):
    try:
        enc_record = DataEncryption.query.get(encryption_id)
        if not enc_record:
            return jsonify({'error': 'Encryption record not found'}), 404
        
        plaintext = EncryptionBackupService.decrypt_data(enc_record.ciphertext, enc_record.nonce, enc_record.tag, enc_record.key_id)
        
        audit_log = AuditLog(
            action='DECRYPT_DATA',
            entity_type='DataEncryption',
            entity_id=encryption_id,
            user_id=current_user_id,
            details=f'Decrypted data with key {enc_record.key_id}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'plaintext': plaintext}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/create', methods=['POST'])
@token_required
def create_backup(current_user_id):
    try:
        data = request.get_json()
        backup_data = data.get('backup_data')
        location = data.get('location', 'LOCAL')
        
        backup_record, checksum = EncryptionBackupService.create_backup(backup_data, location, current_user_id)
        
        audit_log = AuditLog(
            action='CREATE_BACKUP',
            entity_type='BackupRecord',
            entity_id=backup_record.id,
            user_id=current_user_id,
            details=f'Backup created at {location}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'backup_id': backup_record.id, 'checksum': checksum, 'status': backup_record.status}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/<int:backup_id>/verify', methods=['GET'])
@token_required
def verify_backup(current_user_id, backup_id):
    try:
        backup_record = BackupRecord.query.get(backup_id)
        if not backup_record:
            return jsonify({'error': 'Backup not found'}), 404
        
        integrity_log = EncryptionBackupService.verify_backup_integrity(backup_record)
        
        audit_log = AuditLog(
            action='VERIFY_BACKUP',
            entity_type='BackupRecord',
            entity_id=backup_id,
            user_id=current_user_id,
            details=f'Backup integrity verified: {integrity_log.integrity_verified}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'backup_id': backup_id,
            'integrity_verified': integrity_log.integrity_verified,
            'expected_checksum': integrity_log.checksum_expected,
            'actual_checksum': integrity_log.checksum_actual,
            'recovery_possible': integrity_log.recovery_possible
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@encryption_bp.route('/rotate-key', methods=['POST'])
@token_required
def rotate_encryption_key(current_user_id):
    try:
        data = request.get_json()
        old_key_id = data.get('old_key_id')
        
        new_key = EncryptionBackupService.rotate_encryption_key(old_key_id, current_user_id)
        
        audit_log = AuditLog(
            action='ROTATE_ENCRYPTION_KEY',
            entity_type='EncryptionKey',
            entity_id=new_key.id,
            user_id=current_user_id,
            details=f'Key rotated from {old_key_id} to {new_key.id}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'new_key_id': new_key.id, 'algorithm': new_key.algorithm}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
