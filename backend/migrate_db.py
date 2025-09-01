#!/usr/bin/env python3
"""
Database migration script to add advanced metrics columns.
Run this script to update your existing database with new metrics fields.
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add advanced metrics columns to existing database."""
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    db_path = os.path.join(project_root, "eval_forge.db")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("No migration needed - new database will be created with latest schema.")
        return True
    
    print(f"Migrating database at {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migration is needed by looking for new columns
        cursor.execute("PRAGMA table_info(results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'bleu_score' in columns:
            print("Database already migrated - advanced metrics columns exist.")
            conn.close()
            return True
        
        print("Adding advanced metrics columns to results table...")
        
        # Add new columns to results table
        cursor.execute("ALTER TABLE results ADD COLUMN bleu_score REAL")
        cursor.execute("ALTER TABLE results ADD COLUMN rouge_1_score REAL")
        cursor.execute("ALTER TABLE results ADD COLUMN rouge_2_score REAL")
        cursor.execute("ALTER TABLE results ADD COLUMN rouge_l_score REAL")
        cursor.execute("ALTER TABLE results ADD COLUMN semantic_similarity REAL")
        
        print("Adding advanced metrics columns to evaluations table...")
        
        # Add new columns to evaluations table
        cursor.execute("ALTER TABLE evaluations ADD COLUMN avg_bleu_score REAL")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN avg_rouge_1_score REAL")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN avg_rouge_2_score REAL")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN avg_rouge_l_score REAL")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN avg_semantic_similarity REAL")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN avg_response_time REAL")
        
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        print("Advanced metrics columns have been added to your database.")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
