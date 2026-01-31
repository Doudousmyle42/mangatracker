"""
Migration script to add the missing image_couverture column to existing database
Run this once to fix the database schema
"""
import sqlite3
import os

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "manga.db")

def migrate_database():
    """Add missing image_couverture column if it doesn't exist"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        print("The database will be created automatically when you run the app.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(mangas)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns in 'mangas' table: {columns}")
        
        if 'image_couverture' not in columns:
            print("\n🔧 Adding 'image_couverture' column...")
            cursor.execute("""
                ALTER TABLE mangas 
                ADD COLUMN image_couverture VARCHAR(500)
            """)
            conn.commit()
            print("✅ Column 'image_couverture' added successfully!")
        else:
            print("\n✅ Column 'image_couverture' already exists, no migration needed.")
        
        # Check again to confirm
        cursor.execute("PRAGMA table_info(mangas)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"\nUpdated columns in 'mangas' table: {columns}")
        
    except sqlite3.Error as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE MIGRATION SCRIPT")
    print("=" * 80)
    migrate_database()
    print("=" * 80)