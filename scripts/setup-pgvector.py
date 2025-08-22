#!/usr/bin/env python3
"""
Setup script to enable pgvector extension in PostgreSQL databases
Supports both local development and Cloud SQL environments
"""

import os
import sys
import asyncio
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add project root to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.api.shared.database import get_database_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_pgvector_extension():
    """
    Setup pgvector extension for the configured database
    """
    
    try:
        # Get database configuration
        db_config = get_database_config()
        engine = create_engine(db_config.get_database_url())
        
        logger.info("Connecting to database to setup pgvector extension...")
        
        with engine.connect() as connection:
            # Enable pgvector extension
            logger.info("Enabling pgvector extension...")
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            connection.commit()
            
            # Verify extension is installed
            result = connection.execute(text(
                "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
            ))
            extension_info = result.fetchone()
            
            if extension_info:
                logger.info(f"✅ pgvector extension enabled successfully!")
                logger.info(f"   Extension: {extension_info[0]}")
                logger.info(f"   Version: {extension_info[1]}")
            else:
                logger.error("❌ Failed to enable pgvector extension")
                return False
            
            # Check if tables exist and create vector indexes if needed
            logger.info("Checking for existing tables...")
            
            # Check notes table
            notes_exists = connection.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'notes');"
            )).scalar()
            
            if notes_exists:
                logger.info("Notes table found - creating vector indexes...")
                create_vector_indexes(connection, 'notes', [
                    'title_embedding', 'body_embedding', 'combined_embedding'
                ])
            
            # Check tasks table
            tasks_exists = connection.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tasks');"
            )).scalar()
            
            if tasks_exists:
                logger.info("Tasks table found - creating vector indexes...")
                create_vector_indexes(connection, 'tasks', ['description_embedding'])
            
            connection.commit()
            logger.info("✅ pgvector setup completed successfully!")
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error during pgvector setup: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during pgvector setup: {e}")
        return False

def create_vector_indexes(connection, table_name: str, embedding_columns: list):
    """
    Create vector indexes for better search performance
    """
    
    for column in embedding_columns:
        index_name = f"{table_name}_{column}_idx"
        
        try:
            # Check if index already exists
            index_exists = connection.execute(text(f"""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE tablename = '{table_name}' 
                    AND indexname = '{index_name}'
                );
            """)).scalar()
            
            if not index_exists:
                logger.info(f"Creating vector index: {index_name}")
                
                # Create IVFFlat index for vector similarity search
                # Lists parameter should be roughly rows/1000, but we'll use 100 as default
                connection.execute(text(f"""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} 
                    ON {table_name} 
                    USING ivfflat ({column} vector_cosine_ops) 
                    WITH (lists = 100);
                """))
                
                logger.info(f"✅ Created index: {index_name}")
            else:
                logger.info(f"✅ Index already exists: {index_name}")
                
        except SQLAlchemyError as e:
            logger.warning(f"⚠️ Could not create index {index_name}: {e}")
            # Continue with other indexes even if one fails

def check_pgvector_status():
    """
    Check if pgvector is properly installed and configured
    """
    
    try:
        db_config = get_database_config()
        engine = create_engine(db_config.get_database_url())
        
        with engine.connect() as connection:
            # Check if extension exists
            result = connection.execute(text(
                "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
            ))
            extension_info = result.fetchone()
            
            if not extension_info:
                logger.error("❌ pgvector extension is not installed")
                return False
            
            logger.info(f"✅ pgvector extension found (version: {extension_info[1]})")
            
            # Check vector indexes
            indexes_result = connection.execute(text("""
                SELECT tablename, indexname 
                FROM pg_indexes 
                WHERE indexname LIKE '%_embedding_%'
                ORDER BY tablename, indexname;
            """))
            
            indexes = indexes_result.fetchall()
            if indexes:
                logger.info("✅ Vector indexes found:")
                for table, index in indexes:
                    logger.info(f"   {table}.{index}")
            else:
                logger.warning("⚠️ No vector indexes found")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking pgvector status: {e}")
        return False

def main():
    """Main function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # Check status only
        logger.info("Checking pgvector status...")
        success = check_pgvector_status()
    else:
        # Setup pgvector
        logger.info("Setting up pgvector extension...")
        success = setup_pgvector_extension()
    
    if not success:
        sys.exit(1)
    
    logger.info("🎉 pgvector setup completed successfully!")

if __name__ == "__main__":
    main()