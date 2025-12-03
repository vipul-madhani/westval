"""Seed comprehensive sample data for Westval demonstration"""
import os
import sys
import pymysql
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
import uuid
import random

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
    
    # Get existing users
    cursor.execute("SELECT id, email FROM users")
    users = cursor.fetchall()
    if not users:
        print("No users found. Please run seed_db.py first.")
        sys.exit(1)
    
    admin_id = users[0][0]
    user_id = users[1][0] if len(users) > 1 else admin_id
    
    print(f"\nFound {len(users)} users")
    print(f"Admin ID: {admin_id}")
    print(f"User ID: {user_id}")
    
    # Sample Validation Projects
    projects = [
        {
            'project_number': 'VAL-2025-0001',
            'title': 'ERP System CSV - SAP S/4HANA',
            'description': 'Computerized System Validation for SAP S/4HANA implementation covering Finance, Materials Management, and Quality Management modules.',
            'validation_type': 'CSV',
            'methodology': 'CSA',
            'gamp_category': '5',
            'risk_level': 'High',
            'risk_score': 85,
            'status': 'In Progress',
            'department': 'IT',
            'planned_start': date(2025, 1, 15),
            'planned_end': date(2025, 6, 30),
            'actual_start': date(2025, 1, 20),
            'progress': 65
        },
        {
            'project_number': 'VAL-2025-0002',
            'title': 'LIMS Validation - LabWare v8.5',
            'description': 'Laboratory Information Management System validation for QC laboratory including sample tracking, testing workflows, and results management.',
            'validation_type': 'Lab',
            'methodology': 'Waterfall',
            'gamp_category': '4',
            'risk_level': 'High',
            'risk_score': 78,
            'status': 'Planning',
            'department': 'Quality Control',
            'planned_start': date(2025, 3, 1),
            'planned_end': date(2025, 8, 31),
            'actual_start': None,
            'progress': 15
        },
        {
            'project_number': 'VAL-2025-0003',
            'title': 'Equipment IQ/OQ - Tablet Press',
            'description': 'Installation and Operational Qualification for new Fette P3090 tablet compression machine including all critical parameters and performance criteria.',
            'validation_type': 'Equipment',
            'methodology': 'Waterfall',
            'gamp_category': '1',
            'risk_level': 'Medium',
            'risk_score': 55,
            'status': 'Review',
            'department': 'Manufacturing',
            'planned_start': date(2024, 11, 1),
            'planned_end': date(2025, 2, 28),
            'actual_start': date(2024, 11, 5),
            'progress': 85
        },
        {
            'project_number': 'VAL-2024-0089',
            'title': 'Cleaning Validation - API Manufacturing',
            'description': 'Cleaning validation protocol for Active Pharmaceutical Ingredient manufacturing equipment including reactors, dryers, and milling equipment.',
            'validation_type': 'Cleaning',
            'methodology': 'Waterfall',
            'gamp_category': '1',
            'risk_level': 'High',
            'risk_score': 82,
            'status': 'Approved',
            'department': 'Manufacturing',
            'planned_start': date(2024, 8, 1),
            'planned_end': date(2024, 12, 31),
            'actual_start': date(2024, 8, 5),
            'progress': 100
        },
        {
            'project_number': 'VAL-2025-0004',
            'title': 'Temperature Mapping - Cold Storage',
            'description': 'Temperature distribution study for 2-8°C cold storage room including seasonal variations and door opening impact studies.',
            'validation_type': 'Equipment',
            'methodology': 'Waterfall',
            'gamp_category': '1',
            'risk_level': 'Medium',
            'risk_score': 60,
            'status': 'In Progress',
            'department': 'Quality Assurance',
            'planned_start': date(2025, 2, 1),
            'planned_end': date(2025, 4, 30),
            'actual_start': date(2025, 2, 3),
            'progress': 40
        },
        {
            'project_number': 'VAL-2025-0005',
            'title': 'Data Integrity - Audit Trail Validation',
            'description': 'Comprehensive data integrity assessment and audit trail validation for all GxP systems including LIMS, ERP, and MES.',
            'validation_type': 'CSV',
            'methodology': 'CSA',
            'gamp_category': '5',
            'risk_level': 'Critical',
            'risk_score': 95,
            'status': 'Planning',
            'department': 'Quality Assurance',
            'planned_start': date(2025, 4, 1),
            'planned_end': date(2025, 10, 31),
            'actual_start': None,
            'progress': 10
        },
        {
            'project_number': 'VAL-2025-0006',
            'title': 'MES Integration - Werum PAS-X',
            'description': 'Manufacturing Execution System validation for Werum PAS-X integration with SAP ERP and batch record management.',
            'validation_type': 'CSV',
            'methodology': 'Agile',
            'gamp_category': '5',
            'risk_level': 'High',
            'risk_score': 80,
            'status': 'In Progress',
            'department': 'Manufacturing',
            'planned_start': date(2025, 1, 10),
            'planned_end': date(2025, 7, 31),
            'actual_start': date(2025, 1, 15),
            'progress': 55
        },
        {
            'project_number': 'VAL-2024-0095',
            'title': 'HVAC Qualification - Cleanroom Suite',
            'description': 'HVAC system qualification for ISO Class 7 cleanroom including airflow visualization, filter integrity, and environmental monitoring.',
            'validation_type': 'Equipment',
            'methodology': 'Waterfall',
            'gamp_category': '1',
            'risk_level': 'High',
            'risk_score': 75,
            'status': 'Review',
            'department': 'Engineering',
            'planned_start': date(2024, 10, 1),
            'planned_end': date(2025, 1, 31),
            'actual_start': date(2024, 10, 5),
            'progress': 90
        },
        {
            'project_number': 'VAL-2024-0087',
            'title': 'Water System - Purified Water',
            'description': 'Validation of purified water generation and distribution system including chemical, microbiological, and endotoxin testing.',
            'validation_type': 'Process',
            'methodology': 'Waterfall',
            'gamp_category': '1',
            'risk_level': 'High',
            'risk_score': 85,
            'status': 'Approved',
            'department': 'Engineering',
            'planned_start': date(2024, 6, 1),
            'planned_end': date(2024, 11, 30),
            'actual_start': date(2024, 6, 3),
            'progress': 100
        },
        {
            'project_number': 'VAL-2025-0007',
            'title': 'Autoclave Validation - Sterilization',
            'description': 'Steam sterilization validation for laboratory autoclave including heat distribution, heat penetration, and biological indicator studies.',
            'validation_type': 'Equipment',
            'methodology': 'Waterfall',
            'gamp_category': '1',
            'risk_level': 'Medium',
            'risk_score': 65,
            'status': 'In Progress',
            'department': 'Quality Control',
            'planned_start': date(2025, 2, 15),
            'planned_end': date(2025, 5, 15),
            'actual_start': date(2025, 2, 18),
            'progress': 70
        }
    ]
    
    print("\n" + "="*60)
    print("Creating Validation Projects...")
    print("="*60)
    
    for proj in projects:
        project_id = str(uuid.uuid4())
        owner = admin_id if random.random() > 0.5 else user_id
        
        cursor.execute("""
            INSERT INTO validation_projects (
                id, project_number, title, description, validation_type, methodology,
                gamp_category, risk_level, risk_score, status, owner_id, department,
                planned_start_date, planned_end_date, actual_start_date,
                created_at, updated_at, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE id=id
        """, (
            project_id, proj['project_number'], proj['title'], proj['description'],
            proj['validation_type'], proj['methodology'], proj['gamp_category'],
            proj['risk_level'], proj['risk_score'], proj['status'], owner,
            proj['department'], proj['planned_start'], proj['planned_end'],
            proj['actual_start'], datetime.utcnow(), datetime.utcnow(), admin_id
        ))
        
        print(f"✓ {proj['project_number']}: {proj['title']} ({proj['status']}, {proj['progress']}%)")
    
    conn.commit()
    
    print("\n" + "="*60)
    print("✓ Sample data seeded successfully!")
    print("="*60)
    print(f"\nCreated:")
    print(f"  - {len(projects)} Validation Projects")
    print(f"  - Various types: CSV, Lab, Equipment, Cleaning, Process")
    print(f"  - Various statuses: Planning, In Progress, Review, Approved")
    print("="*60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
