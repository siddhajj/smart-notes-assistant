# Import shared database configuration
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database import get_db, init_db, engine, SessionLocal
from app.models import Base

def init_notes_db():
    """Initialize notes service database tables"""
    init_db(Base)
