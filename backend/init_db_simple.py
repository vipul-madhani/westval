"""Simple database initialization script"""
import os
import sys
import uuid
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['FLASK_APP'] = 'run.py'

from app.extensions import db
from app import create_app

# Import only the core models that exist
try:
    from app.models.user import User, Role
    print("✓ User models imported")
except Exception as e:
    print(f"✗ Error importing user models: {e}")
    User = None
    Role = None

try:
    from app.models.validation import ValidationProject
    print("✓ Validation models imported")
except Exception as e:
    print(f"✗ Error importing validation models: {e}")

try:
    from app.models.test_management import TestPlan, TestSet, TestCase, TestStep, TestExecution, TestStepResult
    print("✓ Test management models imported")
except Exception as e:
    print(f"✗ Error importing test management models: {e}")

try:
    from app.models.document import Document, DocumentVersion
    print("✓ Document models imported")
except Exception as e:
    print(f"✗ Error importing document models: {e}")

try:
    from app.models.requirement import Requirement
    print("✓ Requirement models imported")
except Exception as e:
    print(f"✗ Error importing requirement models: {e}")

try:
    from app.models.risk import RiskAssessment
    print("✓ Risk models imported")
except Exception as e:
    print(f"✗ Error importing risk models: {e}")

try:
    from app.models.workflow import WorkflowTemplate, WorkflowState, WorkflowTransition
    print("✓ Workflow models imported")
except Exception as e:
    print(f"✗ Error importing workflow models: {e}")

try:
    from app.models.audit import AuditLog
    print("✓ Audit models imported")
except Exception as e:
    print(f"✗ Error importing audit models: {e}")

try:
    from app.models.signature import ElectronicSignature
    print("✓ Signature models imported")
except Exception as e:
    print(f"✗ Error importing signature models: {e}")

print("\n" + "="*50)
print("Creating Flask app...")
app = create_app()

with app.app_context():
    print("Creating all database tables...")
    db.create_all()
    print("✓ All tables created successfully!")
    
    # Create default roles
    if Role:
        print("\nCreating default roles...")
        roles_data = [
            {'name': 'Admin', 'description': 'System administrator', 'permissions': ['all']},
            {'name': 'Validator', 'description': 'Validation specialist', 'permissions': ['create_project', 'create_protocol', 'execute_tests']},
            {'name': 'QA', 'description': 'Quality assurance reviewer', 'permissions': ['review_documents', 'approve_protocols']},
            {'name': 'Approver', 'description': 'Final approver', 'permissions': ['approve_documents', 'sign_documents']},
        ]
        
        for role_data in roles_data:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(
                    id=str(uuid.uuid4()),
                    name=role_data['name'],
                    description=role_data['description'],
                    permissions=role_data['permissions']
                )
                db.session.add(role)
                print(f"  ✓ Created role: {role_data['name']}")
    
    # Create default admin user
    if User:
        print("\nCreating default admin user...")
        if not User.query.filter_by(email='admin@westval.com').first():
            admin = User(
                id=str(uuid.uuid4()),
                email='admin@westval.com',
                username='admin',
                first_name='System',
                last_name='Administrator',
                is_admin=True,
                is_active=True,
                department='IT',
                job_title='System Administrator'
            )
            admin.set_password('Admin@Westval2025!')
            db.session.add(admin)
            print("  ✓ Created admin user (admin@westval.com / Admin@Westval2025!)")
    
    db.session.commit()
    print("\n" + "="*50)
    print("✓ Database initialized successfully!")
    print("="*50)
