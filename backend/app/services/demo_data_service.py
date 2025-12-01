"""Demo data initialization service"""
from datetime import datetime, timedelta
import uuid
from app import db
from app.models.user import User, Role
from app.models.validation import ValidationProject, ValidationProtocol
from app.models.requirement import Requirement
from app.models.test import TestCase
from app.models.document import Document
from app.services.workflow_service import WorkflowService

class DemoDataService:
    
    @staticmethod
    def initialize_demo_data():
        """Initialize complete demo data for pharma presentation"""
        print('\n=== Initializing Demo Data ===')
        
        # Create demo users
        users = DemoDataService._create_demo_users()
        print(f'✓ Created {len(users)} demo users')
        
        # Create validation project
        project = DemoDataService._create_demo_project(users['validator'])
        print(f'✓ Created demo project: {project.name}')
        
        # Create requirements
        requirements = DemoDataService._create_demo_requirements(project.id)
        print(f'✓ Created {len(requirements)} requirements')
        
        # Create protocol
        protocol = DemoDataService._create_demo_protocol(project.id, users['validator'])
        print(f'✓ Created protocol: {protocol.protocol_number}')
        
        # Create test cases
        test_cases = DemoDataService._create_demo_test_cases(protocol.id, requirements)
        print(f'✓ Created {len(test_cases)} test cases')
        
        # Create documents
        documents = DemoDataService._create_demo_documents(project.id, users['validator'])
        print(f'✓ Created {len(documents)} documents')
        
        print('\n=== Demo Data Initialized Successfully ===')
        print(f'\nLogin Credentials:')
        print(f'  Email: demo.validator@westval.com')
        print(f'  Password: Demo@2025!')
        print(f'\nProject: {project.name}')
        print(f'Status: {len([t for t in test_cases if t.status == "Passed"])} passed, '
              f'{len([t for t in test_cases if t.status == "Failed"])} failed')
    
    @staticmethod
    def _create_demo_users():
        """Create demo users with different roles"""
        # Get roles
        validator_role = Role.query.filter_by(name='Validator').first()
        qa_role = Role.query.filter_by(name='QA').first()
        approver_role = Role.query.filter_by(name='Approver').first()
        
        users = {}
        
        # Validator
        if not User.query.filter_by(email='demo.validator@westval.com').first():
            validator = User(
                id=str(uuid.uuid4()),
                email='demo.validator@westval.com',
                username='demo_validator',
                first_name='John',
                last_name='Smith',
                is_active=True,
                department='Validation',
                job_title='Senior Validation Engineer'
            )
            validator.set_password('Demo@2025!')
            if validator_role:
                validator.roles.append(validator_role)
            db.session.add(validator)
            users['validator'] = validator
        
        # QA Reviewer
        if not User.query.filter_by(email='demo.qa@westval.com').first():
            qa = User(
                id=str(uuid.uuid4()),
                email='demo.qa@westval.com',
                username='demo_qa',
                first_name='Sarah',
                last_name='Johnson',
                is_active=True,
                department='Quality Assurance',
                job_title='QA Manager'
            )
            qa.set_password('Demo@2025!')
            if qa_role:
                qa.roles.append(qa_role)
            db.session.add(qa)
            users['qa'] = qa
        
        # Approver
        if not User.query.filter_by(email='demo.approver@westval.com').first():
            approver = User(
                id=str(uuid.uuid4()),
                email='demo.approver@westval.com',
                username='demo_approver',
                first_name='Michael',
                last_name='Davis',
                is_active=True,
                department='Quality',
                job_title='Head of Quality'
            )
            approver.set_password('Demo@2025!')
            if approver_role:
                approver.roles.append(approver_role)
            db.session.add(approver)
            users['approver'] = approver
        
        db.session.commit()
        return users
    
    @staticmethod
    def _create_demo_project(creator):
        """Create demo validation project"""
        project = ValidationProject(
            id=str(uuid.uuid4()),
            name='ERP System CSV - SAP Implementation',
            description='Computer System Validation for enterprise SAP ERP implementation',
            validation_type='CSV',
            status='In Progress',
            risk_assessment='Medium',
            start_date=datetime.utcnow() - timedelta(days=30),
            target_completion=datetime.utcnow() + timedelta(days=60),
            project_manager=f'{creator.first_name} {creator.last_name}'
        )
        db.session.add(project)
        db.session.commit()
        return project
    
    @staticmethod
    def _create_demo_requirements(project_id):
        """Create demo requirements"""
        req_data = [
            {'id': 'REQ-001', 'title': 'User Authentication', 'criticality': 'Critical', 'status': 'Verified'},
            {'id': 'REQ-002', 'title': 'Data Export Functionality', 'criticality': 'High', 'status': 'Verified'},
            {'id': 'REQ-003', 'title': 'Password Reset', 'criticality': 'Medium', 'status': 'Not Tested'},
            {'id': 'REQ-004', 'title': 'User Profile Management', 'criticality': 'Low', 'status': 'Verified'},
            {'id': 'REQ-005', 'title': 'Admin Dashboard', 'criticality': 'Critical', 'status': 'Failed'},
            {'id': 'REQ-006', 'title': 'Audit Trail', 'criticality': 'Critical', 'status': 'Verified'},
            {'id': 'REQ-007', 'title': 'Electronic Signatures', 'criticality': 'Critical', 'status': 'Verified'},
        ]
        
        requirements = []
        for req in req_data:
            requirement = Requirement(
                id=str(uuid.uuid4()),
                project_id=project_id,
                requirement_id=req['id'],
                title=req['title'],
                description=f'System shall provide {req["title"].lower()} functionality',
                type='Functional',
                criticality=req['criticality'],
                status=req['status']
            )
            db.session.add(requirement)
            requirements.append(requirement)
        
        db.session.commit()
        return requirements
    
    @staticmethod
    def _create_demo_protocol(project_id, author):
        """Create demo validation protocol"""
        protocol = ValidationProtocol(
            id=str(uuid.uuid4()),
            project_id=project_id,
            protocol_number='VP-SAP-001',
            title='SAP ERP System Installation Qualification',
            protocol_type='IQ',
            status='Approved',
            version='1.0',
            author=f'{author.first_name} {author.last_name}',
            created_date=datetime.utcnow() - timedelta(days=20)
        )
        db.session.add(protocol)
        db.session.commit()
        return protocol
    
    @staticmethod
    def _create_demo_test_cases(protocol_id, requirements):
        """Create demo test cases"""
        test_data = [
            {'id': 'TC-001', 'title': 'Verify User Login', 'req': 'REQ-001', 'status': 'Passed'},
            {'id': 'TC-002', 'title': 'Test Data Export', 'req': 'REQ-002', 'status': 'Passed'},
            {'id': 'TC-003', 'title': 'User Profile Update', 'req': 'REQ-004', 'status': 'Passed'},
            {'id': 'TC-004', 'title': 'Admin Dashboard Load', 'req': 'REQ-005', 'status': 'Failed'},
            {'id': 'TC-005', 'title': 'Audit Trail Capture', 'req': 'REQ-006', 'status': 'Passed'},
            {'id': 'TC-006', 'title': 'Electronic Signature', 'req': 'REQ-007', 'status': 'Passed'},
        ]
        
        test_cases = []
        for test in test_data:
            test_case = TestCase(
                id=str(uuid.uuid4()),
                protocol_id=protocol_id,
                test_case_id=test['id'],
                title=test['title'],
                objective=f'Verify {test["title"].lower()} functionality',
                status=test['status'],
                expected_result='System functions as specified',
                actual_result='As expected' if test['status'] == 'Passed' else 'Dashboard timeout error',
                execution_date=datetime.utcnow() - timedelta(days=5),
                executed_by='John Smith'
            )
            db.session.add(test_case)
            test_cases.append(test_case)
        
        db.session.commit()
        return test_cases
    
    @staticmethod
    def _create_demo_documents(project_id, author):
        """Create demo documents"""
        doc_data = [
            {'id': 'DOC-001', 'title': 'Validation Plan', 'type': 'Validation Plan', 'status': 'Approved'},
            {'id': 'DOC-002', 'title': 'User Requirements Specification', 'type': 'URS', 'status': 'Approved'},
            {'id': 'DOC-003', 'title': 'Risk Assessment', 'type': 'Risk Assessment', 'status': 'Approved'},
        ]
        
        documents = []
        for doc in doc_data:
            document = Document(
                id=str(uuid.uuid4()),
                project_id=project_id,
                document_id=doc['id'],
                title=doc['title'],
                document_type=doc['type'],
                status=doc['status'],
                version='1.0',
                author=f'{author.first_name} {author.last_name}',
                created_date=datetime.utcnow() - timedelta(days=25)
            )
            db.session.add(document)
            documents.append(document)
        
        db.session.commit()
        return documents