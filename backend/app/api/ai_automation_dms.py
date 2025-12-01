from flask import Blueprint, request, jsonify
from functools import wraps
from ai_automation_dms_service import AIAutomationDMSService

ai_dms_bp = Blueprint('ai_dms', __name__, url_prefix='/api/ai-dms')

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing authorization'}), 401
        return f(*args, **kwargs)
    return decorated_function

# QMS Document Upload & Management
@ai_dms_bp.route('/documents/upload', methods=['POST'])
@require_auth
def upload_qms_document():
    '''Upload QMS document (SOP, WorkInstruction, Form)'''
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type')  # SOP, WorkInstruction, Form
        document_version = request.form.get('document_version', '1.0')
        
        file_content = file.read()
        qms_doc = AIAutomationDMSService.upload_qms_document(
            filename=file.filename,
            file_content=file_content,
            document_type=document_type,
            document_version=document_version,
            uploaded_by=request.headers.get('User-ID')
        )
        return jsonify({'document': qms_doc}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai_dms_bp.route('/documents/<doc_id>', methods=['GET'])
@require_auth
def get_qms_document(doc_id):
    '''Retrieve QMS document details and extracted text'''
    return jsonify({'doc_id': doc_id, 'status': 'Retrieved'}), 200

# AI Extraction
@ai_dms_bp.route('/extract/<doc_id>', methods=['POST'])
@require_auth
def trigger_ai_extraction(doc_id):
    '''Trigger GPT-4 extraction on QMS document'''
    try:
        confidence_threshold = request.json.get('confidence_threshold', 0.7)
        # Extract from document
        extractions = AIAutomationDMSService.gpt4_extract_requirements(
            document_text='Sample SOP content',
            confidence_threshold=confidence_threshold
        )
        return jsonify({'extractions': extractions, 'total': len(extractions)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai_dms_bp.route('/extractions/<extraction_id>', methods=['GET'])
@require_auth
def get_extraction(extraction_id):
    '''Retrieve AI extraction with validation status'''
    return jsonify({'extraction_id': extraction_id}), 200

@ai_dms_bp.route('/extractions/<extraction_id>/validate', methods=['POST'])
@require_auth
def validate_extraction(extraction_id):
    '''Human validation of AI extraction'''
    try:
        data = request.json
        validation_notes = data.get('validation_notes')
        return jsonify({'extraction_id': extraction_id, 'validated': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Requirements Generation
@ai_dms_bp.route('/requirements/generate', methods=['POST'])
@require_auth
def generate_requirements_from_extraction():
    '''Convert AI extraction to structured requirements'''
    try:
        data = request.json
        extraction_id = data.get('extraction_id')
        extracted_text = data.get('extracted_text')
        
        requirements = AIAutomationDMSService.generate_requirements_from_extraction(
            extraction_id=extraction_id,
            extracted_text=extracted_text
        )
        return jsonify({'requirements': requirements}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai_dms_bp.route('/requirements/<req_id>', methods=['GET'])
@require_auth
def get_requirement(req_id):
    '''Retrieve requirement with acceptance criteria and risk assessment'''
    return jsonify({'requirement_id': req_id}), 200

# Template Generation
@ai_dms_bp.route('/templates/generate', methods=['POST'])
@require_auth
def generate_template_from_requirements():
    '''Generate test plan from requirements'''
    try:
        data = request.json
        requirements = data.get('requirements', [])
        
        template = AIAutomationDMSService.generate_test_plan_from_requirements(
            requirements=requirements
        )
        return jsonify({'template': template}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai_dms_bp.route('/templates/<template_id>/approve', methods=['POST'])
@require_auth
def approve_template(template_id):
    '''Business approval of AI-generated template'''
    try:
        data = request.json
        approval_notes = data.get('approval_notes')
        
        approval = AIAutomationDMSService.approve_template_for_production(
            template_id=template_id,
            approved_by=request.headers.get('User-ID'),
            approval_notes=approval_notes
        )
        return jsonify({'approval': approval}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# DMS Migration
@ai_dms_bp.route('/migrate', methods=['POST'])
@require_auth
def migrate_to_dms():
    '''Migrate approved template to production DMS'''
    try:
        data = request.json
        template_id = data.get('template_id')
        qms_document_id = data.get('qms_document_id')
        
        dms_doc = AIAutomationDMSService.migrate_to_dms(
            template_id=template_id,
            qms_document_id=qms_document_id
        )
        return jsonify({'dms_document': dms_doc}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai_dms_bp.route('/dms/<dms_id>', methods=['GET'])
@require_auth
def get_dms_document(dms_id):
    '''Retrieve migrated DMS document'''
    return jsonify({'dms_id': dms_id}), 200

# Traceability & Audit
@ai_dms_bp.route('/traceability/<dms_id>', methods=['GET'])
@require_auth
def get_traceability_chain(dms_id):
    '''Get complete QMS → AI → Requirement → Test → Report traceability'''
    traceability = AIAutomationDMSService.get_full_traceability_chain(dms_id)
    return jsonify({'traceability': traceability}), 200

# Quality Assurance
@ai_dms_bp.route('/quality/validate', methods=['POST'])
@require_auth
def validate_extraction_quality():
    '''Validate AI extraction quality score'''
    try:
        data = request.json
        is_valid, score, issues = AIAutomationDMSService.validate_extraction_quality(data)
        return jsonify({
            'valid': is_valid,
            'quality_score': score,
            'issues': issues
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Health Check
@ai_dms_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'ai-dms'}), 200
