"""
Fix the character_inventory table by creating it with the equipped column.
Run this once to update your database.
"""

import sqlite3

def fix_inventory_table():
    """Create or recreate the character_inventory table with the equipped column."""
    
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='character_inventory'
    """)
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        print("Table character_inventory exists, checking for equipped column...")
        
        # Check if equipped column exists
        cursor.execute("PRAGMA table_info(character_inventory)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'equipped' not in column_names:
            print("Adding equipped column to existing table...")
            cursor.execute("""
                ALTER TABLE character_inventory 
                ADD COLUMN equipped INTEGER NOT NULL DEFAULT 0
            """)
            print("Added equipped column to character_inventory table")
        else:
            print("equipped column already exists")
    else:
        print("Creating character_inventory table...")
        cursor.execute("""
            CREATE TABLE character_inventory (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                weight_lb REAL NOT NULL DEFAULT 0.0,
                description TEXT,
                value_gp REAL NOT NULL DEFAULT 0,
                equipped INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        """)
        
        # Create index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_character_inventory_character_id 
            ON character_inventory(character_id)
        """)
        
        print("Created character_inventory table with equipped column")
    
    conn.commit()
    conn.close()
    print("\nDatabase fixed! You can now create characters with equipment.")

if __name__ == "__main__":
    fix_inventory_table()