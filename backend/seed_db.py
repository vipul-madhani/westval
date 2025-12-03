"""Ultra-simple database seeding script"""
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

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
    
    # Helper to get or create role
    def get_or_create_role(name, description, permissions):
        cursor.execute("SELECT id FROM roles WHERE name = %s", (name,))
        result = cursor.fetchone()
        if result:
            print(f"Role '{name}' already exists.")
            return result[0]
        
        new_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO roles (id, name, description, permissions, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_id, name, description, permissions, datetime.utcnow()))
        print(f"Created role '{name}'.")
        return new_id

    # Helper to get or create user
    def get_or_create_user(email, username, password, first_name, last_name, is_admin, job_title):
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            print(f"User '{email}' already exists.")
            return result[0]
            
        new_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (id, email, username, password_hash, first_name, last_name, 
                              is_admin, is_active, is_locked, is_ldap_user, department, job_title, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (new_id, email, username, password_hash, first_name, last_name,
              is_admin, True, False, False, 'IT' if is_admin else 'Quality', job_title, datetime.utcnow(), datetime.utcnow()))
        print(f"Created user '{email}'.")
        return new_id

    # Helper to assign role
    def assign_role(user_id, role_id):
        cursor.execute("SELECT id FROM user_roles WHERE user_id = %s AND role_id = %s", (user_id, role_id))
        if cursor.fetchone():
            return
            
        cursor.execute("""
            INSERT INTO user_roles (id, user_id, role_id, assigned_at)
            VALUES (%s, %s, %s, %s)
        """, (str(uuid.uuid4()), user_id, role_id, datetime.utcnow()))
        print(f"Assigned role to user.")

    # Create roles
    admin_role_id = get_or_create_role('Admin', 'System administrator', '["all"]')
    engineer_role_id = get_or_create_role('Validation Engineer', 'Standard user for validation activities', '["read", "write", "execute"]')

    # Create users
    admin_id = get_or_create_user('admin@westval.com', 'admin', 'Admin@Westval2025!', 'System', 'Administrator', True, 'System Administrator')
    user_id = get_or_create_user('user@westval.com', 'user', 'User@Westval2025!', 'Val', 'Engineer', False, 'Validation Engineer')
    
    # Assign roles
    assign_role(admin_id, admin_role_id)
    assign_role(user_id, engineer_role_id)
    
    conn.commit()
    
    print("\n" + "="*50)
    print("✓ Database seeded successfully!")
    print("="*50)
    print("\nLogin credentials:")
    print("  1. Admin User (Configuration & System)")
    print("     Email: admin@westval.com")
    print("     Password: Admin@Westval2025!")
    print("\n  2. Validation Engineer (Day-to-day Work)")
    print("     Email: user@westval.com")
    print("     Password: User@Westval2025!")
    print("="*50)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error seeding database: {e}")
    import traceback
    traceback.print_exc()
