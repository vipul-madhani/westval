"""AI-powered features API - Complete implementation"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()

@ai_bp.route('/generate-protocol', methods=['POST'])
@jwt_required()
def generate_protocol():
    """AI-generated validation protocol"""
    data = request.get_json()
    
    if not data.get('template_type') or not data.get('project_data'):
        return jsonify({'error': 'template_type and project_data are required'}), 400
    
    try:
        protocol_content = ai_service.generate_protocol(
            data['template_type'],
            data['project_data']
        )
        
        return jsonify({
            'message': 'Protocol generated successfully',
            'protocol': protocol_content
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/generate-test-cases', methods=['POST'])
@jwt_required()
def generate_test_cases():
    """AI-generated test cases from requirements"""
    data = request.get_json()
    
    if not data.get('requirements'):
        return jsonify({'error': 'requirements are required'}), 400
    
    try:
        test_cases = ai_service.generate_test_cases(data['requirements'])
        
        return jsonify({
            'message': 'Test cases generated successfully',
            'test_cases': test_cases,
            'count': len(test_cases)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/review-document', methods=['POST'])
@jwt_required()
def review_document():
    """AI document review and gap analysis"""
    data = request.get_json()
    
    if not data.get('content') or not data.get('document_type'):
        return jsonify({'error': 'content and document_type are required'}), 400
    
    try:
        review_results = ai_service.review_document(
            data['content'],
            data['document_type']
        )
        
        return jsonify({
            'message': 'Document review completed',
            'review': review_results
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/assess-risk', methods=['POST'])
@jwt_required()
def assess_risk():
    """AI-powered risk assessment"""
    data = request.get_json()
    
    if not data.get('system_description'):
        return jsonify({'error': 'system_description is required'}), 400
    
    try:
        risk_assessment = ai_service.assess_risk(data['system_description'])
        
        return jsonify({
            'message': 'Risk assessment completed',
            'risks': risk_assessment
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500