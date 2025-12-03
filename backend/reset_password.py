import os
import sys
import pymysql
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

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
    
    admin_pass = generate_password_hash('Admin@Westval2025!')
    user_pass = generate_password_hash('User@Westval2025!')
    
    print("Resetting Admin password...")
    cursor.execute("UPDATE users SET password_hash = %s WHERE email = 'admin@westval.com'", (admin_pass,))
    
    print("Resetting User password...")
    cursor.execute("UPDATE users SET password_hash = %s WHERE email = 'user@westval.com'", (user_pass,))
    
    conn.commit()
    print("Passwords reset successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
