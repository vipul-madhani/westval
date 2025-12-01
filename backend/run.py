"""Application entry point"""
from app import create_app, db, socketio
from app.models.user import User, Role
import uuid

app = create_app()

@app.cli.command()
def init_db():
    """Initialize database with default data"""
    db.create_all()
    
    # Create default roles
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
    
    # Create default admin user
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
    
    db.session.commit()
    print('Database initialized successfully!')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)