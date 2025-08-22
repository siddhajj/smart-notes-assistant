from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    body = Column(Text)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # References users.id from user-service
    
    # Embedding fields for semantic search
    title_embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small dimension
    body_embedding = Column(Vector(1536))
    combined_embedding = Column(Vector(1536))  # Combined title + body embedding
    
    # Metadata for embeddings
    embedding_model = Column(String, default="text-embedding-3-small")
    embedding_created_at = Column(DateTime, default=datetime.utcnow)
    
    # Search metadata
    tags = Column(ARRAY(String))  # User-defined tags for categorization
    content_hash = Column(String)  # Hash of content to detect changes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # This relationship assumes a 'users' table exists and is managed by a separate service
    # For a true microservice architecture, you might not have a direct ORM relationship here
    # and would instead fetch user details via API calls to the user service.
    # For simplicity in this example, we'll assume a shared 'users' table or a mechanism
    # to ensure user_id validity.
    # owner = relationship("User", back_populates="notes")
