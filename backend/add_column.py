import os
import sys
import pymysql
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
    
    print("Adding is_ldap_user column to users table...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_ldap_user BOOLEAN DEFAULT FALSE")
        conn.commit()
        print("Column added successfully!")
    except pymysql.err.OperationalError as e:
        if "Duplicate column name" in str(e):
            print("Column already exists.")
        else:
            raise e
            
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
