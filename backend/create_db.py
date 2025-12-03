import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 8889))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME = os.getenv('DB_NAME', 'westval')

print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT} as {DB_USER}...")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    print(f"Creating database '{DB_NAME}' if it doesn't exist...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    
    print("Database created successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error creating database: {e}")
