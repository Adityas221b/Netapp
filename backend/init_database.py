"""
CloudFlux AI - Database Initialization Script
Creates all tables in PostgreSQL
"""
import sys
sys.path.insert(0, '.')

from app.database import init_db, engine
from app.models import User, DataObject, MigrationJob, AuditLog, MLModelMetrics, CostSnapshot
from sqlalchemy import inspect

def main():
    print("🚀 Initializing CloudFlux AI Database...")
    print("="*60)
    
    # Create all tables
    init_db()
    
    # Verify tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n✅ Created {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")
    
    print("\n="*60)
    print("✅ Database initialization complete!")
    print("\n📊 You can now run queries against PostgreSQL")
    print("   Connection: postgresql://cloudflux:cloudflux123@localhost:5432/cloudflux")

if __name__ == "__main__":
    main()
