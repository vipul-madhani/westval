import hashlib
import os
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
from app.models.encryption_backup import DataEncryption, BackupRecord, BackupIntegrityLog, EncryptionKey, EncryptionAlgorithm, BackupStatus, BackupLocation
from app import db

class EncryptionBackupService:
    KEY_SIZE = 32
    IV_SIZE = 16
    SALT_SIZE = 16
    TAG_SIZE = 16
    
    @staticmethod
    def derive_key(password, salt):
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=EncryptionBackupService.KEY_SIZE,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    @staticmethod
    def encrypt_data(data, key_id, user_id, algorithm=EncryptionAlgorithm.AES_256_GCM):
        try:
            if isinstance(data, str):
                data_bytes = data.encode()
            else:
                data_bytes = data
            
            data_hash_before = hashlib.sha256(data_bytes).hexdigest()
            
            iv = os.urandom(EncryptionBackupService.IV_SIZE)
            cipher = Cipher(
                algorithms.AES(key_id.encode().ljust(EncryptionBackupService.KEY_SIZE)[:EncryptionBackupService.KEY_SIZE]),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(data_bytes) + encryptor.finalize()
            
            data_hash_after = hashlib.sha256(encrypted_data).hexdigest()
            
            encryption = DataEncryption(
                record_id=hashlib.sha256(encrypted_data).hexdigest()[:32],
                record_type='BACKUP',
                encrypted_data=encrypted_data,
                encryption_key_id=key_id,
                algorithm=algorithm,
                initialization_vector=base64.b64encode(iv).decode(),
                authentication_tag=base64.b64encode(encryptor.tag).decode(),
                data_hash_before=data_hash_before,
                data_hash_after=data_hash_after,
                encrypted_by_id=user_id,
                encryption_timestamp=datetime.utcnow(),
                is_valid=True
            )
            db.session.add(encryption)
            db.session.commit()
            return encryption
        except Exception as e:
            return None
    
    @staticmethod
    def decrypt_data(encryption_id, key_id):
        try:
            encryption = DataEncryption.query.get(encryption_id)
            if not encryption or not encryption.is_valid:
                return None
            
            iv = base64.b64decode(encryption.initialization_vector)
            tag = base64.b64decode(encryption.authentication_tag)
            
            cipher = Cipher(
                algorithms.AES(key_id.encode().ljust(EncryptionBackupService.KEY_SIZE)[:EncryptionBackupService.KEY_SIZE]),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encryption.encrypted_data) + decryptor.finalize()
            
            encryption.decryption_attempts += 1
            encryption.last_decryption = datetime.utcnow()
            db.session.commit()
            
            return decrypted_data
        except Exception:
            return None
    
    @staticmethod
    def create_backup(database_name, backup_type, backup_path, backup_size, key_id, user_id, location=BackupLocation.LOCAL):
        checksum = hashlib.sha256(backup_path.encode()).hexdigest()
        backup = BackupRecord(
            backup_type=backup_type,
            database_name=database_name,
            backup_size_bytes=backup_size,
            backup_location=location,
            backup_path=backup_path,
            status=BackupStatus.COMPLETED,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            encryption_key_id=key_id,
            encryption_algorithm=EncryptionAlgorithm.AES_256_GCM,
            backup_checksum=checksum,
            retention_days=30,
            expiry_date=datetime.utcnow() + timedelta(days=30),
            created_by_id=user_id,
            status=BackupStatus.VERIFIED
        )
        db.session.add(backup)
        db.session.commit()
        return backup
    
    @staticmethod
    def verify_backup_integrity(backup_id, expected_checksum, user_id):
        backup = BackupRecord.query.get(backup_id)
        if not backup:
            return None
        
        integrity_verified = backup.backup_checksum == expected_checksum
        
        log = BackupIntegrityLog(
            backup_id=backup_id,
            verification_timestamp=datetime.utcnow(),
            verification_status='PASSED' if integrity_verified else 'FAILED',
            checksum_expected=expected_checksum,
            checksum_actual=backup.backup_checksum,
            integrity_verified=integrity_verified,
            total_files_checked=1,
            files_corrupted=0 if integrity_verified else 1,
            recovery_possible=integrity_verified,
            verified_by_id=user_id
        )
        db.session.add(log)
        
        if integrity_verified:
            backup.status = BackupStatus.VERIFIED
        else:
            backup.status = BackupStatus.FAILED
        
        db.session.commit()
        return log
    
    @staticmethod
    def rotate_encryption_key(old_key_id, new_key_id, user_id):
        old_key = EncryptionKey.query.filter_by(key_identifier=old_key_id).first()
        if old_key:
            old_key.is_active = False
            old_key.rotation_date = datetime.utcnow()
        
        new_key = EncryptionKey(
            key_identifier=new_key_id,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_version=1,
            is_active=True,
            created_by_id=user_id
        )
        db.session.add(new_key)
        db.session.commit()
        return new_key
