from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.digital_signature import DigitalCertificate, DigitalSignature
from app.services.digital_signature_service import DigitalSignatureService
from app.models.document import Document
from app import db
from datetime import datetime

digital_signature_bp = Blueprint('digital_signature', __name__, url_prefix='/api/signatures')

@digital_signature_bp.route('/certificate/generate', methods=['POST'])
@jwt_required()
def generate_certificate():
    user_id = get_jwt_identity()
    data = request.get_json()
    subject_cn = data.get('subject_cn')
    days_valid = data.get('days_valid', 365)
    if not subject_cn:
        return jsonify({"error": "subject_cn required"}), 400
    try:
        cert = DigitalSignatureService.create_certificate_record(
            subject_cn=subject_cn,
            user_id=user_id,
            created_by_id=user_id,
            days_valid=days_valid
        )
        return jsonify({
            "id": cert.id,
            "thumbprint": cert.thumbprint,
            "status": cert.status.value,
            "expiry_date": cert.expiry_date.isoformat()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@digital_signature_bp.route('/certificate/<cert_id>', methods=['GET'])
@jwt_required()
def get_certificate(cert_id):
    cert = DigitalCertificate.query.get(cert_id)
    if not cert:
        return jsonify({"error": "Certificate not found"}), 404
    return jsonify({
        "id": cert.id,
        "subject_dn": cert.subject_dn,
        "issuer_dn": cert.issuer_dn,
        "serial_number": cert.serial_number,
        "thumbprint": cert.thumbprint,
        "status": cert.status.value,
        "issued_date": cert.issued_date.isoformat(),
        "expiry_date": cert.expiry_date.isoformat()
    }), 200

@digital_signature_bp.route('/sign', methods=['POST'])
@jwt_required()
def sign_document():
    user_id = get_jwt_identity()
    data = request.get_json()
    document_id = data.get('document_id')
    document_data = data.get('document_data')
    certificate_id = data.get('certificate_id')
    if not all([document_id, document_data, certificate_id]):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        cert = DigitalCertificate.query.get(certificate_id)
        if not cert:
            return jsonify({"error": "Certificate not found"}), 404
        if cert.status.value == "REVOKED":
            return jsonify({"error": "Certificate is revoked"}), 400
        signature_value = DigitalSignatureService.sign_document(
            document_data, cert.private_key_pem
        )
        signature_hash = DigitalSignatureService.compute_signature_hash(signature_value)
        sig = DigitalSignature(
            document_id=document_id,
            document_type="PDF",
            signature_value=signature_value,
            signature_hash=signature_hash,
            certificate_id=certificate_id,
            signed_by_id=user_id,
            signature_timestamp=datetime.utcnow(),
            algorithm=cert.algorithm,
            is_valid=True
        )
        db.session.add(sig)
        db.session.commit()
        return jsonify({
            "id": sig.id,
            "signature_hash": signature_hash,
            "signed_at": sig.signature_timestamp.isoformat()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@digital_signature_bp.route('/<sig_id>/verify', methods=['POST'])
@jwt_required()
def verify_signature(sig_id):
    data = request.get_json()
    document_data = data.get('document_data')
    if not document_data:
        return jsonify({"error": "document_data required"}), 400
    try:
        sig = DigitalSignature.query.get(sig_id)
        if not sig:
            return jsonify({"error": "Signature not found"}), 404
        cert = DigitalCertificate.query.get(sig.certificate_id)
        if not cert:
            return jsonify({"error": "Certificate not found"}), 404
        is_valid = DigitalSignatureService.verify_signature(
            document_data, sig.signature_value, cert.public_key_pem
        )
        sig.is_valid = is_valid
        sig.validation_timestamp = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "valid": is_valid,
            "signature_id": sig_id,
            "certificate_thumbprint": cert.thumbprint,
            "signed_by": sig.signed_by_id,
            "signed_at": sig.signature_timestamp.isoformat()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@digital_signature_bp.route('/certificate/<cert_id>/revoke', methods=['POST'])
@jwt_required()
def revoke_certificate(cert_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    reason = data.get('reason')
    if not reason:
        return jsonify({"error": "reason required"}), 400
    try:
        revocation = DigitalSignatureService.revoke_certificate(
            cert_id, user_id, reason
        )
        if not revocation:
            return jsonify({"error": "Certificate not found"}), 404
        return jsonify({
            "revoked_at": revocation.revoked_at.isoformat(),
            "reason": revocation.reason
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
