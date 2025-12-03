"""Seed comprehensive test management sample data"""
import os
import sys
import pymysql
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid
import random
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 8889))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME = os.getenv('DB_NAME', 'westval')

print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT}...")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    # Get existing users and projects
    cursor.execute("SELECT id FROM users LIMIT 2")
    users = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM validation_projects LIMIT 5")
    projects = [row[0] for row in cursor.fetchall()]
    
    if not users or not projects:
        print("Need users and projects. Run seed_sample_data.py first.")
        sys.exit(1)
    
    print(f"\nFound {len(users)} users and {len(projects)} projects")
    
    # Test Plans
    test_plans = [
        {
            'name': 'ERP System Installation Qualification (IQ)',
            'description': 'Installation qualification test plan for SAP S/4HANA covering hardware, software, and network configuration verification.',
            'status': 'Active',
            'project_id': projects[0]
        },
        {
            'name': 'LIMS Operational Qualification (OQ)',
            'description': 'Operational qualification test plan for LabWare LIMS covering all functional modules and workflows.',
            'status': 'Active',
            'project_id': projects[1] if len(projects) > 1 else projects[0]
        },
        {
            'name': 'Equipment Performance Qualification (PQ)',
            'description': 'Performance qualification test plan for tablet press equipment covering all critical performance parameters.',
            'status': 'Completed',
            'project_id': projects[2] if len(projects) > 2 else projects[0]
        },
        {
            'name': 'Data Integrity Testing',
            'description': 'Comprehensive data integrity test plan covering audit trails, electronic signatures, and data security.',
            'status': 'Draft',
            'project_id': projects[3] if len(projects) > 3 else projects[0]
        },
        {
            'name': 'User Acceptance Testing (UAT)',
            'description': 'User acceptance testing for MES system covering end-user workflows and business processes.',
            'status': 'Active',
            'project_id': projects[4] if len(projects) > 4 else projects[0]
        }
    ]
    
    print("\n" + "="*60)
    print("Creating Test Plans...")
    print("="*60)
    
    plan_ids = []
    for plan in test_plans:
        plan_id = str(uuid.uuid4())
        plan_ids.append(plan_id)
        
        cursor.execute("""
            INSERT INTO test_plans (id, project_id, name, description, status, created_by, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE id=id
        """, (
            plan_id, plan['project_id'], plan['name'], plan['description'],
            plan['status'], users[0], datetime.utcnow(), datetime.utcnow()
        ))
        
        print(f"✓ {plan['name']} ({plan['status']})")
    
    # Test Cases with Steps
    test_cases_data = [
        # IQ Test Cases (Plan 1)
        {
            'plan_idx': 0,
            'name': 'TC-IQ-001: Verify Server Hardware Specifications',
            'description': 'Verify that the server hardware meets the specified requirements for CPU, RAM, and storage.',
            'test_type': 'Functional',
            'priority': 1,
            'steps': [
                {'action': 'Check CPU specifications', 'expected': 'CPU meets minimum requirements (16 cores, 2.5GHz)'},
                {'action': 'Check RAM capacity', 'expected': 'RAM is 64GB or higher'},
                {'action': 'Check storage capacity', 'expected': 'Storage is 2TB SSD or higher'}
            ]
        },
        {
            'plan_idx': 0,
            'name': 'TC-IQ-002: Verify Operating System Installation',
            'description': 'Verify that the operating system is correctly installed and configured.',
            'test_type': 'Functional',
            'priority': 1,
            'steps': [
                {'action': 'Check OS version', 'expected': 'Red Hat Enterprise Linux 8.5 installed'},
                {'action': 'Verify OS patches', 'expected': 'All security patches applied'},
                {'action': 'Check system services', 'expected': 'All required services running'}
            ]
        },
        {
            'plan_idx': 0,
            'name': 'TC-IQ-003: Verify Database Installation',
            'description': 'Verify that the database is correctly installed and accessible.',
            'test_type': 'Functional',
            'priority': 1,
            'steps': [
                {'action': 'Check database version', 'expected': 'Oracle 19c installed'},
                {'action': 'Verify database connectivity', 'expected': 'Can connect to database'},
                {'action': 'Check database configuration', 'expected': 'Configuration matches specifications'}
            ]
        },
        
        # OQ Test Cases (Plan 2)
        {
            'plan_idx': 1,
            'name': 'TC-OQ-001: Sample Login and Navigation',
            'description': 'Verify that users can log in and navigate through the LIMS system.',
            'test_type': 'Functional',
            'priority': 1,
            'steps': [
                {'action': 'Enter valid credentials', 'expected': 'Login successful'},
                {'action': 'Navigate to Sample Management', 'expected': 'Sample Management module opens'},
                {'action': 'Navigate to Test Management', 'expected': 'Test Management module opens'}
            ]
        },
        {
            'plan_idx': 1,
            'name': 'TC-OQ-002: Sample Registration',
            'description': 'Verify that samples can be registered in the system.',
            'test_type': 'Functional',
            'priority': 1,
            'steps': [
                {'action': 'Click New Sample button', 'expected': 'Sample registration form opens'},
                {'action': 'Enter sample details', 'expected': 'All fields accept input'},
                {'action': 'Save sample', 'expected': 'Sample saved with unique ID'}
            ]
        },
        
        # PQ Test Cases (Plan 3)
        {
            'plan_idx': 2,
            'name': 'TC-PQ-001: Tablet Weight Uniformity',
            'description': 'Verify that tablet weight uniformity meets specifications.',
            'test_type': 'Performance',
            'priority': 1,
            'steps': [
                {'action': 'Weigh 20 tablets individually', 'expected': 'All weights recorded'},
                {'action': 'Calculate average weight', 'expected': 'Average within 98-102% of target'},
                {'action': 'Check individual variations', 'expected': 'No tablet deviates >5% from average'}
            ]
        },
        
        # Data Integrity Test Cases (Plan 4)
        {
            'plan_idx': 3,
            'name': 'TC-DI-001: Audit Trail Completeness',
            'description': 'Verify that all user actions are recorded in the audit trail.',
            'test_type': 'Security',
            'priority': 1,
            'steps': [
                {'action': 'Perform create operation', 'expected': 'Audit log created with WHO, WHAT, WHEN'},
                {'action': 'Perform update operation', 'expected': 'Audit log shows old and new values'},
                {'action': 'Perform delete operation', 'expected': 'Audit log shows deletion with reason'}
            ]
        },
        
        # UAT Test Cases (Plan 5)
        {
            'plan_idx': 4,
            'name': 'TC-UAT-001: Batch Record Creation',
            'description': 'Verify that users can create batch records in the MES system.',
            'test_type': 'Functional',
            'priority': 2,
            'steps': [
                {'action': 'Navigate to Batch Records', 'expected': 'Batch Records screen opens'},
                {'action': 'Click New Batch', 'expected': 'Batch creation wizard starts'},
                {'action': 'Complete batch details', 'expected': 'Batch record created successfully'}
            ]
        }
    ]
    
    print("\n" + "="*60)
    print("Creating Test Cases and Steps...")
    print("="*60)
    
    case_ids = []
    for case_data in test_cases_data:
        case_id = str(uuid.uuid4())
        case_ids.append(case_id)
        
        cursor.execute("""
            INSERT INTO test_cases (
                id, plan_id, name, description, test_type, priority, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE id=id
        """, (
            case_id, plan_ids[case_data['plan_idx']], case_data['name'],
            case_data['description'], case_data['test_type'], case_data['priority'],
            'Active', datetime.utcnow()
        ))
        
        # Add test steps
        for idx, step in enumerate(case_data['steps'], 1):
            step_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO test_steps (
                    id, test_case_id, step_number, action, expected_result, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE id=id
            """, (
                step_id, case_id, idx, step['action'], step['expected'], datetime.utcnow()
            ))
        
        print(f"✓ {case_data['name']} ({len(case_data['steps'])} steps)")
    
    # Test Executions
    print("\n" + "="*60)
    print("Creating Test Executions...")
    print("="*60)
    
    execution_count = 0
    for i, case_id in enumerate(case_ids[:8]):  # Execute first 8 test cases
        execution_id = str(uuid.uuid4())
        
        # Get test case steps
        cursor.execute("SELECT id FROM test_steps WHERE test_case_id = %s ORDER BY step_number", (case_id,))
        step_ids = [row[0] for row in cursor.fetchall()]
        
        total_steps = len(step_ids)
        passed = random.randint(max(0, total_steps-2), total_steps)
        failed = total_steps - passed
        overall_status = 'PASS' if failed == 0 else 'FAIL'
        
        cursor.execute("""
            INSERT INTO test_executions (
                id, test_case_id, execution_date, executed_by, total_steps,
                passed_steps, failed_steps, overall_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE id=id
        """, (
            execution_id, case_id, datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            random.choice(users), total_steps, passed, failed, overall_status, datetime.utcnow()
        ))
        
        # Create step results
        for step_id in step_ids:
            result_id = str(uuid.uuid4())
            step_status = 'PASS' if passed > 0 else 'FAIL'
            if step_status == 'PASS':
                passed -= 1
            
            cursor.execute("""
                INSERT INTO test_step_results (
                    id, execution_id, step_id, status, actual_result, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE id=id
            """, (
                result_id, execution_id, step_id, step_status,
                'Step executed as expected' if step_status == 'PASS' else 'Step failed - see notes',
                datetime.utcnow()
            ))
        
        execution_count += 1
        print(f"✓ Execution {execution_count}: {overall_status} ({total_steps} steps)")
    
    conn.commit()
    
    print("\n" + "="*60)
    print("✓ Test Management data seeded successfully!")
    print("="*60)
    print(f"\nCreated:")
    print(f"  - {len(test_plans)} Test Plans")
    print(f"  - {len(test_cases_data)} Test Cases")
    print(f"  - {sum(len(tc['steps']) for tc in test_cases_data)} Test Steps")
    print(f"  - {execution_count} Test Executions")
    print("="*60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
