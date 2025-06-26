#!/usr/bin/env python3
"""
Apply Vector Search Migration Script
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.core.database import supabase_admin

def apply_vector_migration():
    """Apply the vector search migration to Supabase"""
    
    migration_file = Path(__file__).parent / "database" / "migrations" / "003_vector_search.sql"
    
    print("📦 Applying Vector Search Migration...")
    print(f"📄 Reading migration from: {migration_file}")
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_content = f.read()
        
        # Split into individual statements
        sql_statements = []
        current_statement = ""
        
        for line in migration_content.split('\n'):
            if line.strip().startswith('--') or not line.strip():
                continue
            
            current_statement += line + '\n'
            
            if line.strip().endswith(';'):
                if current_statement.strip():
                    sql_statements.append(current_statement.strip())
                current_statement = ""
        
        print(f"🔧 Found {len(sql_statements)} SQL statements to execute")
        
        success_count = 0
        skip_count = 0
        
        for i, statement in enumerate(sql_statements, 1):
            if not statement.strip():
                continue
                
            print(f"\n📋 Executing statement {i}/{len(sql_statements)}")
            print(f"   {statement[:100]}{'...' if len(statement) > 100 else ''}")
            
            try:
                result = supabase_admin.rpc('exec_sql', {
                    'query': statement
                }).execute()
                
                print(f"✅ Statement {i} executed successfully")
                success_count += 1
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's an expected error (already exists)
                if any(phrase in error_msg for phrase in [
                    'already exists', 
                    'relation already exists',
                    'constraint already exists',
                    'index already exists',
                    'column already exists',
                    'extension already exists'
                ]):
                    print(f"⚠️  Statement {i} skipped (already exists)")
                    skip_count += 1
                else:
                    print(f"❌ Statement {i} failed: {str(e)[:200]}")
                    # Continue with other statements
        
        print(f"\n🎉 Migration completed!")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ⚠️  Skipped: {skip_count}")
        print(f"   ❌ Failed: {len(sql_statements) - success_count - skip_count}")
        
        # Test if pgvector extension is available
        print("\n🔍 Testing pgvector extension...")
        try:
            test_result = supabase_admin.rpc('exec_sql', {
                'query': "SELECT extname FROM pg_extension WHERE extname = 'vector';"
            }).execute()
            
            if test_result.data and len(test_result.data) > 0:
                print("✅ pgvector extension is installed and available")
            else:
                print("❌ pgvector extension not found - vector search may not work")
                
        except Exception as e:
            print(f"⚠️  Could not verify pgvector: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = apply_vector_migration()
    sys.exit(0 if success else 1)
