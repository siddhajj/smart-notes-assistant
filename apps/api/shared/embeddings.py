import hashlib
import logging
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import openai
from google.cloud import aiplatform
import os

logger = logging.getLogger(__name__)

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name used by this provider"""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension"""
        pass

class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider using text-embedding-3-small"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = openai.AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self._model_name = "text-embedding-3-small"
        self._dimension = 1536
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self._model_name
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=self._model_name
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            raise
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def dimension(self) -> int:
        return self._dimension

class VertexAIEmbeddingProvider(EmbeddingProvider):
    """Vertex AI embedding provider using textembedding-gecko"""
    
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self._model_name = "textembedding-gecko@003"
        self._dimension = 768
        
        if self.project_id:
            aiplatform.init(project=self.project_id, location=self.location)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            from vertexai.language_models import TextEmbeddingModel
            model = TextEmbeddingModel.from_pretrained(self._model_name)
            embeddings = model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
            logger.error(f"Error generating Vertex AI embedding: {e}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            from vertexai.language_models import TextEmbeddingModel
            model = TextEmbeddingModel.from_pretrained(self._model_name)
            embeddings = model.get_embeddings(texts)
            return [emb.values for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating Vertex AI embeddings: {e}")
            raise
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def dimension(self) -> int:
        return self._dimension

class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider for testing and local development"""
    
    def __init__(self, dimension: int = 1536):
        self._model_name = "mock-embedding-model"
        self._dimension = dimension
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a deterministic mock embedding based on text hash"""
        import random
        
        # Use text hash as seed for deterministic results
        seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Generate normalized random vector
        embedding = [random.gauss(0, 1) for _ in range(self._dimension)]
        
        # Normalize the vector
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for multiple texts"""
        return [await self.generate_embedding(text) for text in texts]
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def dimension(self) -> int:
        return self._dimension

class EmbeddingService:
    """Main embedding service that manages different providers"""
    
    def __init__(self, provider: Optional[EmbeddingProvider] = None):
        self.provider = provider or self._get_default_provider()
    
    def _get_default_provider(self) -> EmbeddingProvider:
        """Get the default embedding provider based on environment"""
        
        # Check for OpenAI API key
        if os.getenv("OPENAI_API_KEY"):
            logger.info("Using OpenAI embedding provider")
            return OpenAIEmbeddingProvider()
        
        # Check for GCP project
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            logger.info("Using Vertex AI embedding provider")
            return VertexAIEmbeddingProvider()
        
        # Fallback to mock provider
        logger.info("Using mock embedding provider for local development")
        return MockEmbeddingProvider()
    
    async def generate_text_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.provider.dimension
        
        return await self.provider.generate_embedding(text.strip())
    
    async def generate_combined_embedding(self, title: str, body: str) -> List[float]:
        """Generate embedding for combined title and body text"""
        # Combine title and body with proper formatting
        combined_text = f"{title}\n\n{body}" if title and body else (title or body or "")
        return await self.generate_text_embedding(combined_text)
    
    async def generate_note_embeddings(self, title: str, body: str) -> Dict[str, List[float]]:
        """Generate all embeddings for a note"""
        title_embedding = await self.generate_text_embedding(title or "")
        body_embedding = await self.generate_text_embedding(body or "")
        combined_embedding = await self.generate_combined_embedding(title, body)
        
        return {
            "title_embedding": title_embedding,
            "body_embedding": body_embedding,
            "combined_embedding": combined_embedding
        }
    
    async def generate_task_embedding(self, description: str) -> List[float]:
        """Generate embedding for a task description"""
        return await self.generate_text_embedding(description or "")
    
    def generate_content_hash(self, *texts: str) -> str:
        """Generate a hash of the content to detect changes"""
        content = "|".join(text or "" for text in texts)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @property
    def model_name(self) -> str:
        """Get the current model name"""
        return self.provider.model_name
    
    @property
    def dimension(self) -> int:
        """Get the embedding dimension"""
        return self.provider.dimension

# Global embedding service instance
_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def set_embedding_service(service: EmbeddingService) -> None:
    """Set the global embedding service instance"""
    global _embedding_service
    _embedding_service = service