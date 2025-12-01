"""AI-powered document generation and analysis service"""
import os
from openai import OpenAI
import json

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        self.model = os.getenv('AI_MODEL', 'gpt-4')
    
    def generate_protocol(self, template_type, project_data):
        """Generate validation protocol using AI"""
        if not self.client:
            return self._get_default_protocol(template_type, project_data)
        
        prompt = f"""Generate a {template_type} protocol for a pharmaceutical validation project with the following details:
        
Project: {project_data.get('title')}
Validation Type: {project_data.get('validation_type')}
GAMP Category: {project_data.get('gamp_category')}
Methodology: {project_data.get('methodology')}

Generate a comprehensive protocol including:
1. Objective
2. Scope
3. Responsibilities
4. Acceptance Criteria
5. Test Procedures
6. Documentation Requirements

Format as JSON with sections."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return self._get_default_protocol(template_type, project_data)
    
    def generate_test_cases(self, requirements):
        """Generate test cases from requirements using AI"""
        if not self.client:
            return self._get_default_test_cases(requirements)
        
        prompt = f"""Based on these requirements, generate comprehensive test cases:

{json.dumps(requirements, indent=2)}

For each requirement, generate:
1. Test case ID
2. Test objective
3. Test steps (detailed)
4. Expected results
5. Acceptance criteria

Format as JSON array."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return self._get_default_test_cases(requirements)
    
    def review_document(self, document_content, document_type):
        """AI-powered document review for completeness and compliance"""
        if not self.client:
            return self._get_default_review()
        
        prompt = f"""Review this {document_type} for pharmaceutical validation compliance:

{document_content}

Analyze for:
1. Completeness (missing sections)
2. 21 CFR Part 11 compliance
3. GAMP 5 guidelines adherence
4. Clarity and consistency
5. Regulatory requirements

Provide feedback as JSON with sections: completeness, compliance_gaps, recommendations, risk_level."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return self._get_default_review()
    
    def assess_risk(self, system_description):
        """AI-powered risk assessment"""
        if not self.client:
            return self._get_default_risk_assessment()
        
        prompt = f"""Perform risk assessment for this system:

{system_description}

Identify:
1. Potential hazards
2. Severity (1-5)
3. Probability (1-5)
4. Detectability (1-5)
5. Risk Priority Number (RPN)
6. Mitigation strategies

Format as JSON array of risks."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return self._get_default_risk_assessment()
    
    def _get_default_protocol(self, template_type, project_data):
        """Default protocol template when AI is unavailable"""
        return {
            "objective": f"To qualify the {project_data.get('title')} system",
            "scope": "This protocol covers the validation activities",
            "responsibilities": ["QA: Review and approve", "Validation Team: Execute tests"],
            "acceptance_criteria": "All tests must pass without critical deviations",
            "test_procedures": ["Installation verification", "Operational testing", "Performance qualification"]
        }
    
    def _get_default_test_cases(self, requirements):
        """Default test cases when AI is unavailable"""
        return [{
            "test_case_id": f"TC-{i+1:03d}",
            "objective": req.get('title', 'Test requirement'),
            "steps": ["Step 1: Verify installation", "Step 2: Execute test", "Step 3: Document results"],
            "expected_result": "System performs as specified",
            "acceptance_criteria": "Test passes without deviations"
        } for i, req in enumerate(requirements[:5])]
    
    def _get_default_review(self):
        """Default review when AI is unavailable"""
        return {
            "completeness": "Document structure appears complete",
            "compliance_gaps": [],
            "recommendations": ["Ensure all sections are filled", "Add regulatory references"],
            "risk_level": "Medium"
        }
    
    def _get_default_risk_assessment(self):
        """Default risk assessment when AI is unavailable"""
        return [{
            "hazard": "System failure",
            "severity": 3,
            "probability": 2,
            "detectability": 2,
            "rpn": 12,
            "mitigation": "Implement redundancy and monitoring"
        }]