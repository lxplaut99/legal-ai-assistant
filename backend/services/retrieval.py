from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from models import DocumentChunk, Document
from services.embedding import generate_embedding


async def vector_search(
    query_embedding: list[float],
    db: AsyncSession,
    limit: int = 10,
    document_ids: list[str] | None = None,
) -> list[dict]:
    """Search for similar chunks using pgvector cosine distance."""
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    filters = ""
    if document_ids:
        ids = ",".join(f"'{did}'" for did in document_ids)
        filters = f"AND dc.document_id IN ({ids})"

    query = text(f"""
        SELECT dc.id, dc.document_id, dc.content, dc.page_number, dc.section,
               dc.chunk_index, d.filename,
               dc.embedding <=> :embedding AS distance
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE dc.embedding IS NOT NULL {filters}
        ORDER BY dc.embedding <=> :embedding
        LIMIT :limit
    """)

    result = await db.execute(query, {"embedding": embedding_str, "limit": limit})
    rows = result.mappings().all()

    return [
        {
            "chunk_id": str(row["id"]),
            "document_id": str(row["document_id"]),
            "filename": row["filename"],
            "content": row["content"],
            "page_number": row["page_number"],
            "section": row["section"],
            "chunk_index": row["chunk_index"],
            "score": 1 - float(row["distance"]),  # Convert distance to similarity
        }
        for row in rows
    ]


async def keyword_search(
    query: str,
    db: AsyncSession,
    limit: int = 10,
    document_ids: list[str] | None = None,
) -> list[dict]:
    """Full-text search using PostgreSQL tsvector."""
    filters = ""
    if document_ids:
        ids = ",".join(f"'{did}'" for did in document_ids)
        filters = f"AND dc.document_id IN ({ids})"

    sql = text(f"""
        SELECT dc.id, dc.document_id, dc.content, dc.page_number, dc.section,
               dc.chunk_index, d.filename,
               ts_rank(to_tsvector('english', dc.content), plainto_tsquery('english', :query)) AS rank
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE to_tsvector('english', dc.content) @@ plainto_tsquery('english', :query) {filters}
        ORDER BY rank DESC
        LIMIT :limit
    """)

    result = await db.execute(sql, {"query": query, "limit": limit})
    rows = result.mappings().all()

    return [
        {
            "chunk_id": str(row["id"]),
            "document_id": str(row["document_id"]),
            "filename": row["filename"],
            "content": row["content"],
            "page_number": row["page_number"],
            "section": row["section"],
            "chunk_index": row["chunk_index"],
            "score": float(row["rank"]),
        }
        for row in rows
    ]


async def hybrid_search(
    query: str,
    db: AsyncSession,
    limit: int = 8,
    document_ids: list[str] | None = None,
) -> list[dict]:
    """Combine vector and keyword search results with reciprocal rank fusion."""
    query_embedding = await generate_embedding(query)

    vector_results = await vector_search(query_embedding, db, limit=limit * 2, document_ids=document_ids)
    keyword_results = await keyword_search(query, db, limit=limit * 2, document_ids=document_ids)

    # Reciprocal Rank Fusion
    k = 60  # RRF constant
    scores: dict[str, float] = {}
    chunk_data: dict[str, dict] = {}

    for rank, result in enumerate(vector_results):
        cid = result["chunk_id"]
        scores[cid] = scores.get(cid, 0) + 1 / (k + rank + 1)
        chunk_data[cid] = result

    for rank, result in enumerate(keyword_results):
        cid = result["chunk_id"]
        scores[cid] = scores.get(cid, 0) + 1 / (k + rank + 1)
        chunk_data[cid] = result

    # Sort by fused score and return top results
    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)[:limit]

    results = []
    for cid in sorted_ids:
        entry = chunk_data[cid].copy()
        entry["score"] = scores[cid]
        results.append(entry)

    return results
