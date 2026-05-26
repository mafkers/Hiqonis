import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from libs.infrastructure.database.models import Base, Tenant, KnowledgeBase, Document, DocumentStatus, DocumentChunk
from libs.infrastructure.search.rag_service import RAGService

# Setup in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@pytest.mark.asyncio
async def test_rag_ingest_and_chunking():
    # 1. Initialize tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestSessionLocal() as db:
        # 2. Setup mock Tenant, KB and Document
        tenant = Tenant(name="Hiqonis Testing")
        db.add(tenant)
        await db.flush()
        
        kb = KnowledgeBase(tenant_id=tenant.id, name="Hiqonis KB")
        db.add(kb)
        await db.flush()
        
        doc = Document(
            kb_id=kb.id,
            name="Platform Guide",
            doc_type="text",
            path_or_url="http://test.com",
            status=DocumentStatus.PROCESSING
        )
        db.add(doc)
        await db.commit()
        
        # 3. Instantiate RAG Service
        rag = RAGService(api_key=None)  # Uses mock embeddings (all zeros) during test
        
        # 4. Ingest raw text
        raw_text = (
            "Hiqonis is a standalone enterprise-grade open source AI CX platform. "
            "It runs on Python backend and Next.js frontend and provides instant zero vendor lock-in."
        )
        success = await rag.ingest_document(db, doc.id, raw_text)
        assert success is True
        
        # 5. Verify chunk entries are created in database
        result = await db.execute(select(DocumentChunk).filter(DocumentChunk.document_id == doc.id))
        chunks = list(result.scalars().all())
        assert len(chunks) > 0
        assert chunks[0].content is not None
        assert len(chunks[0].embedding) == 1536
        
        # 6. Verify document status is marked ACTIVE
        result_doc = await db.execute(select(Document).filter(Document.id == doc.id))
        updated_doc = result_doc.scalars().first()
        assert updated_doc.status == DocumentStatus.ACTIVE
