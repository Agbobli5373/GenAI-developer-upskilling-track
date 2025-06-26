"""
Database Migration Runner for Week 2

This script helps apply the document processing migration to Supabase.
"""

import os
from pathlib import Path

def show_migration_sql():
    """Display the migration SQL that needs to be applied to Supabase"""
    
    migration_file = Path("database/migrations/002_document_processing.sql")
    
    if migration_file.exists():
        print("📄 Week 2 Database Migration SQL:")
        print("=" * 60)
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        print("=" * 60)
        print("\n🔧 To apply this migration:")
        print("1. Open your Supabase Dashboard")
        print("2. Go to SQL Editor")  
        print("3. Copy and paste the SQL above")
        print("4. Click 'Run'")
        print("\n✅ After migration, your database will support:")
        print("   • Document processing status tracking")
        print("   • Document chunks with positional information")
        print("   • Full-text search capabilities")
        print("   • Legal document structure analysis")
        
    else:
        print("❌ Migration file not found!")
        print(f"Expected: {migration_file.absolute()}")

if __name__ == "__main__":
    print("🚀 Week 2 Database Migration Setup\n")
    show_migration_sql()
