#!/usr/bin/env python3
"""
Database migration script to add missing synthetic monitoring columns.
Run this script to update your existing database with new synthetic monitoring fields.
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add missing synthetic monitoring columns to existing database."""
    
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
        
        migrations_applied = []
        
        # Check and migrate synthetic_tests table
        cursor.execute("PRAGMA table_info(synthetic_tests)")
        columns = [column[1] for column in cursor.fetchall()]
        
        missing_synthetic_test_columns = []
        expected_columns = [
            ('service_name', 'TEXT'),
            ('auth_type', 'TEXT DEFAULT "none"'),
            ('auth_credentials', 'TEXT'),
            ('ssl_check_enabled', 'BOOLEAN DEFAULT 0'),
            ('alert_thresholds', 'TEXT'),
            ('browser_steps', 'TEXT')
        ]
        
        for col_name, col_def in expected_columns:
            if col_name not in columns:
                missing_synthetic_test_columns.append((col_name, col_def))
        
        if missing_synthetic_test_columns:
            print("Adding missing columns to synthetic_tests table...")
            for col_name, col_def in missing_synthetic_test_columns:
                try:
                    cursor.execute(f"ALTER TABLE synthetic_tests ADD COLUMN {col_name} {col_def}")
                    migrations_applied.append(f"Added {col_name} to synthetic_tests")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        raise
        
        # Check and migrate synthetic_executions table
        cursor.execute("PRAGMA table_info(synthetic_executions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        missing_execution_columns = []
        expected_execution_columns = [
            ('details', 'TEXT'),
            ('connect_time', 'REAL'),
            ('ssl_time', 'REAL'),
            ('first_byte_time', 'REAL')
        ]
        
        for col_name, col_def in expected_execution_columns:
            if col_name not in columns:
                missing_execution_columns.append((col_name, col_def))
        
        if missing_execution_columns:
            print("Adding missing columns to synthetic_executions table...")
            for col_name, col_def in missing_execution_columns:
                try:
                    cursor.execute(f"ALTER TABLE synthetic_executions ADD COLUMN {col_name} {col_def}")
                    migrations_applied.append(f"Added {col_name} to synthetic_executions")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        raise
        
        # Create external_apps table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='external_apps'")
        if not cursor.fetchone():
            print("Creating external_apps table...")
            cursor.execute('''
                CREATE TABLE external_apps (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    service_name TEXT,
                    base_url TEXT,
                    description TEXT,
                    auth_type TEXT DEFAULT "none",
                    auth_credentials TEXT,
                    health_endpoint TEXT DEFAULT "/health",
                    timeout INTEGER DEFAULT 30,
                    ssl_check_enabled BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            ''')
            migrations_applied.append("Created external_apps table")
        
        # Migrate legacy metrics columns if they exist
        cursor.execute("PRAGMA table_info(results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        legacy_metrics_columns = [
            ('bleu_score', 'REAL'),
            ('rouge_1_score', 'REAL'),
            ('rouge_2_score', 'REAL'),
            ('rouge_l_score', 'REAL'),
            ('semantic_similarity', 'REAL')
        ]
        
        for col_name, col_def in legacy_metrics_columns:
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE results ADD COLUMN {col_name} {col_def}")
                    migrations_applied.append(f"Added {col_name} to results")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        raise
        
        # Migrate legacy evaluation columns
        cursor.execute("PRAGMA table_info(evaluations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        legacy_eval_columns = [
            ('avg_bleu_score', 'REAL'),
            ('avg_rouge_1_score', 'REAL'),
            ('avg_rouge_2_score', 'REAL'),
            ('avg_rouge_l_score', 'REAL'),
            ('avg_semantic_similarity', 'REAL'),
            ('avg_response_time', 'REAL')
        ]
        
        for col_name, col_def in legacy_eval_columns:
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE evaluations ADD COLUMN {col_name} {col_def}")
                    migrations_applied.append(f"Added {col_name} to evaluations")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        raise
        
        conn.commit()
        conn.close()
        
        if migrations_applied:
            print("✅ Database migration completed successfully!")
            for migration in migrations_applied:
                print(f"  - {migration}")
        else:
            print("✅ Database is already up to date - no migrations needed.")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
