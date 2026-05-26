import os
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from google import genai

from libs.infrastructure.database.models import Document, DocumentChunk, DocumentStatus

class RAGService:
    """Service to manage document chunking, embedding generation, and vector retrieval."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        # Initialize Google GenAI client
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        
    def set_client(self, api_key: str):
        """Update or set the GenAI client with a new API key."""
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        
    async def get_embedding(self, text: str) -> List[float]:
        """Compute text vector embeddings using Google's text-embedding-004 model."""
        if not self.client:
            # Return a mock 1536-dim vector if API key is missing during local test runs
            return [0.0] * 1536
            
        response = self.client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values

    def chunk_text(self, text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[str]:
        """Split text into overlapping chunks for indexing."""
        chunks = []
        if not text:
            return chunks
            
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunks.append(text[start:end])
            start += (chunk_size - chunk_overlap)
            
        return chunks

    async def ingest_document(
        self, 
        db: AsyncSession, 
        document_id: str, 
        raw_text: str
    ) -> bool:
        """Ingest, chunk, embed, and store a raw text document."""
        # Retrieve the document record
        result = await db.execute(select(Document).filter(Document.id == document_id))
        doc = result.scalars().first()
        if not doc:
            return False
            
        try:
            # 1. Chunk text
            chunks = self.chunk_text(raw_text)
            
            # 2. Compute embeddings and create DocumentChunk entries
            for chunk_content in chunks:
                vector = await self.get_embedding(chunk_content)
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk_content,
                    embedding=vector
                )
                db.add(db_chunk)
                
            # 3. Update document status to Active
            doc.status = DocumentStatus.ACTIVE
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            doc.status = DocumentStatus.FAILED
            await db.commit()
            raise

    async def retrieve_relevant_chunks(
        self, 
        db: AsyncSession, 
        kb_id: str, 
        query: str, 
        limit: int = 4
    ) -> List[DocumentChunk]:
        """Perform semantic pgvector similarity search matching a query to knowledge base chunks."""
        # 1. Generate query embedding vector
        query_vector = await self.get_embedding(query)
        
        # 2. Join DocumentChunk with Document to filter on the correct knowledge base ID
        stmt = (
            select(DocumentChunk)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(Document.kb_id == kb_id)
            .filter(Document.status == DocumentStatus.ACTIVE)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
