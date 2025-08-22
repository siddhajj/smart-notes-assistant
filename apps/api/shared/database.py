"""
Shared database configuration for all microservices
Supports both local development and Cloud SQL production deployment
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
import logging
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import secretmanager

logger = logging.getLogger(__name__)

# Configuration from environment
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("REGION", "us-central1")
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "notes-app-db")
DB_NAME = os.getenv("DB_NAME", "notesapp")
DB_USER = os.getenv("DB_USER", "notesapp_user")

# For local development, use direct DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_secret(secret_name: str) -> str:
    """Retrieve secret from Google Secret Manager"""
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
    
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        raise

def get_cloud_sql_engine():
    """Create SQLAlchemy engine using Cloud SQL Python Connector"""
    if not all([PROJECT_ID, INSTANCE_NAME, DB_NAME, DB_USER]):
        raise ValueError("Missing required Cloud SQL environment variables")
    
    try:
        # Get database password from Secret Manager
        db_password = get_secret("db-password")
        
        # Initialize Cloud SQL Python Connector
        connector = Connector()
        
        def getconn():
            conn = connector.connect(
                f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}",
                "pg8000",
                user=DB_USER,
                password=db_password,
                db=DB_NAME,
                ip_type=IPTypes.PUBLIC
            )
            return conn
        
        # Create SQLAlchemy engine
        engine = create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            poolclass=NullPool,
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
        
        logger.info(f"Connected to Cloud SQL: {PROJECT_ID}:{REGION}:{INSTANCE_NAME}")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create Cloud SQL engine: {e}")
        raise

def get_local_engine():
    """Create SQLAlchemy engine for local development"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set for local development")
    
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("DB_ECHO", "false").lower() == "true"
    )
    
    logger.info(f"Connected to local database: {DATABASE_URL}")
    return engine

def create_engine_for_environment():
    """Create appropriate SQLAlchemy engine based on environment"""
    # If DATABASE_URL is set, use local/direct connection (development)
    if DATABASE_URL:
        return get_local_engine()
    
    # If running in GCP with project ID, use Cloud SQL
    if PROJECT_ID:
        return get_cloud_sql_engine()
    
    # Fallback error
    raise ValueError(
        "Unable to determine database configuration. Set either:\n"
        "1. DATABASE_URL for local development, or\n"
        "2. GOOGLE_CLOUD_PROJECT and related vars for Cloud SQL"
    )

# Create global engine and session factory
try:
    engine = create_engine_for_environment()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database engine: {e}")
    raise

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(base):
    """Initialize database tables"""
    try:
        base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise