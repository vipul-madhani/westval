import hashlib
import hmac
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography import x509
from cryptography.x509.oid import NameOID, AuthorityInformationAccessOID
from cryptography.hazmat.backends import default_backend
import json
from app.models.digital_signature import DigitalCertificate, DigitalSignature, SignatureRevocation, SignatureAlgorithm, CertificateStatus
from app import db

class DigitalSignatureService:
    RSA_KEY_SIZE_2048 = 2048
    RSA_KEY_SIZE_4096 = 4096
    HASH_ALGORITHM = hashes.SHA256()
    PADDING_PSS = lambda: padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)

    @staticmethod
    def generate_rsa_keypair(key_size=2048):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        return private_pem, public_pem

    @staticmethod
    def create_x509_certificate(private_key_pem, subject_cn, issuer_cn, days_valid=365):
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None, backend=default_backend()
        )
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)])
        issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn)])
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=days_valid)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).sign(private_key, DigitalSignatureService.HASH_ALGORITHM, default_backend())
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
        return cert_pem, cert.serial_number

    @staticmethod
    def sign_document(document_data, private_key_pem, algorithm=SignatureAlgorithm.RSA_2048):
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None, backend=default_backend()
        )
        if isinstance(document_data, str):
            document_data = document_data.encode()
        if algorithm in [SignatureAlgorithm.RSA_2048, SignatureAlgorithm.RSA_4096]:
            signature = private_key.sign(
                document_data,
                DigitalSignatureService.PADDING_PSS(),
                DigitalSignatureService.HASH_ALGORITHM
            )
        return signature.hex()

    @staticmethod
    def verify_signature(document_data, signature_hex, public_key_pem, algorithm=SignatureAlgorithm.RSA_2048):
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(), backend=default_backend()
            )
            if isinstance(document_data, str):
                document_data = document_data.encode()
            signature = bytes.fromhex(signature_hex)
            public_key.verify(
                signature,
                document_data,
                DigitalSignatureService.PADDING_PSS(),
                DigitalSignatureService.HASH_ALGORITHM
            )
            return True
        except Exception:
            return False

    @staticmethod
    def compute_signature_hash(signature_value):
        if isinstance(signature_value, str):
            signature_value = signature_value.encode()
        return hashlib.sha256(signature_value).hexdigest()

    @staticmethod
    def create_certificate_record(subject_cn, user_id, created_by_id, days_valid=365, algorithm=SignatureAlgorithm.RSA_2048):
        private_pem, public_pem = DigitalSignatureService.generate_rsa_keypair(
            DigitalSignatureService.RSA_KEY_SIZE_2048 if algorithm == SignatureAlgorithm.RSA_2048 else DigitalSignatureService.RSA_KEY_SIZE_4096
        )
        cert_pem, serial_num = DigitalSignatureService.create_x509_certificate(
            private_pem, subject_cn, "Westval-CA", days_valid
        )
        thumbprint = DigitalSignatureService.compute_signature_hash(cert_pem)[:32]
        certificate = DigitalCertificate(
            certificate_pem=cert_pem,
            public_key_pem=public_pem,
            private_key_pem=private_pem,
            subject_dn=f"CN={subject_cn}",
            issuer_dn="CN=Westval-CA",
            serial_number=str(serial_num),
            issued_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=days_valid),
            thumbprint=thumbprint,
            algorithm=algorithm,
            status=CertificateStatus.VALID,
            is_ca=False,
            key_length=DigitalSignatureService.RSA_KEY_SIZE_2048 if algorithm == SignatureAlgorithm.RSA_2048 else DigitalSignatureService.RSA_KEY_SIZE_4096,
            user_id=user_id,
            created_by_id=created_by_id
        )
        db.session.add(certificate)
        db.session.commit()
        return certificate

    @staticmethod
    def revoke_certificate(certificate_id, revoked_by_id, reason, crl_entry_number=1):
        certificate = DigitalCertificate.query.get(certificate_id)
        if not certificate:
            return None
        certificate.status = CertificateStatus.REVOKED
        revocation = SignatureRevocation(
            certificate_id=certificate_id,
            revoked_at=datetime.utcnow(),
            revoked_by_id=revoked_by_id,
            reason=reason,
            crl_entry_number=crl_entry_number,
            revocation_timestamp=datetime.utcnow()
        )
        db.session.add(revocation)
        db.session.commit()
        return revocation
