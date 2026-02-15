from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# Import app and db
from app import app, db
from models import WellLogFile, CurveData, AIInterpretation

def init_db():
    """Initialize database migrations"""
    try:
        with app.app_context():
            init()
        print("✓ Database migrations initialized")
    except Exception as e:
        print(f"✗ Error initializing migrations: {e}")

def create_migration(message="Auto migration"):
    """Create a new migration"""
    try:
        with app.app_context():
            migrate(message=message)
        print(f"✓ Migration created: {message}")
    except Exception as e:
        print(f"✗ Error creating migration: {e}")

def upgrade_db():
    """Apply migrations to database"""
    try:
        with app.app_context():
            upgrade()
        print("✓ Database upgraded successfully")
    except Exception as e:
        print(f"✗ Error upgrading database: {e}")

def create_tables():
    """Create all database tables"""
    try:
        with app.app_context():
            db.create_all()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manage.py [init|migrate|upgrade|create]")
        print("  init    - Initialize migrations")
        print("  migrate - Create new migration")
        print("  upgrade - Apply migrations")
        print("  create  - Create all tables directly")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'migrate':
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
        create_migration(message)
    elif command == 'upgrade':
        upgrade_db()
    elif command == 'create':
        create_tables()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
