import sqlite3, json
conn = sqlite3.connect("talekeeper.db")
cur = conn.cursor()
cur.execute('PRAGMA table_info(equipment)')
cols = [dict(zip(['cid','name','type','notnull','dflt','pk'], row)) for row in cur.fetchall()]
print(json.dumps(cols, indent=2))
