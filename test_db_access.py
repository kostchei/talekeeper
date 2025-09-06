import sqlite3

try:
    conn = sqlite3.connect('talekeeper.db', timeout=5)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM characters")
    result = cursor.fetchone()
    print(f"Database accessible. Character count: {result[0]}")
    conn.close()
except Exception as e:
    print(f"Database error: {e}")