from apps.api.shared.database import get_database_config

def init_search_db():
    """Initialize search service database configuration"""
    # Search service uses the same database configuration as other services
    # since it searches across notes and tasks tables
    get_database_config()

def get_db():
    """Get database session for search service"""
    from apps.api.shared.database import get_db as shared_get_db
    return shared_get_db()