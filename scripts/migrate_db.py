"""
Database migration script: adding user_id field
Run this script once to update existing database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, SessionLocal

def migrate_database():
    """Adds user_id field to existing tables"""
    db = SessionLocal()
    try:
        # Check if user_id field exists in habits table
        result = db.execute(text("PRAGMA table_info(habits)"))
        columns = [row[1] for row in result]
        
        if 'user_id' not in columns:
            print("Adding user_id field to habits table...")
            # Set default user_id for existing records
            db.execute(text("ALTER TABLE habits ADD COLUMN user_id TEXT DEFAULT 'default_user'"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id)"))
            db.commit()
            print("✓ user_id field added to habits table")
        else:
            print("✓ user_id field already exists in habits table")
        
        # Check if user_id field exists in completions table
        result = db.execute(text("PRAGMA table_info(completions)"))
        columns = [row[1] for row in result]
        
        if 'user_id' not in columns:
            print("Adding user_id field to completions table...")
            # Set default user_id for existing records
            db.execute(text("ALTER TABLE completions ADD COLUMN user_id TEXT DEFAULT 'default_user'"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_completions_user_id ON completions(user_id)"))
            db.commit()
            print("✓ user_id field added to completions table")
        else:
            print("✓ user_id field already exists in completions table")
        
        print("\nMigration completed successfully!")
        print("WARNING: All existing data has been linked to user_id='default_user'")
        print("For production, it's recommended to delete old DB and create new one")
        
    except Exception as e:
        print(f"Migration error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database()

