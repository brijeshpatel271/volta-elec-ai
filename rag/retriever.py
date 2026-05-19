"""
rag/retriever.py
Retrieves relevant knowledge chunks and injects them into the LLM prompt.
This is the core of the RAG pipeline.
"""

from .ingestor import query_knowledge, get_store_stats


# How many knowledge chunks to inject per query
TOP_K = 5

# Minimum relevance score (cosine distance — lower = more relevant)
MAX_DISTANCE = 0.75


def format_context_block(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a clean context block
    for injection into the system prompt.
    """
    if not chunks:
        return ""

    lines = ["=" * 60]
    lines.append("RETRIEVED KNOWLEDGE BASE CONTEXT")
    lines.append("(Use this information to answer accurately. Cite the source title when referencing it.)")
    lines.append("=" * 60)
    lines.append("")

    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        title = meta.get("title", "Unknown Source")
        domain = meta.get("domain", "")
        url = meta.get("url", "")
        distance = chunk.get("distance", 0)

        relevance = "High" if distance < 0.3 else "Medium" if distance < 0.55 else "Low"

        lines.append(f"[Source {i}] {title}")
        if domain:
            lines.append(f"Domain: {domain} | Relevance: {relevance}")
        if url:
            lines.append(f"URL: {url}")
        lines.append("-" * 40)
        lines.append(chunk["text"])
        lines.append("")

    lines.append("=" * 60)
    lines.append("END OF RETRIEVED CONTEXT")
    lines.append("=" * 60)

    return "\n".join(lines)


def build_rag_system_prompt(base_prompt: str, user_query: str, domain_filter: str = None) -> tuple[str, list[dict]]:
    """
    Retrieve relevant chunks and build an augmented system prompt.

    Args:
        base_prompt: The base VOLTA system prompt
        user_query: The user's question
        domain_filter: Optional engineering domain to filter results

    Returns:
        (augmented_system_prompt, retrieved_chunks)
    """
    stats = get_store_stats()

    # No knowledge base yet — return base prompt unchanged
    if stats["status"] in ("not_installed", "empty", "error"):
        return base_prompt, []

    # Retrieve relevant chunks
    chunks = query_knowledge(
        query=user_query,
        n_results=TOP_K,
        domain_filter=domain_filter if domain_filter != "All" else None,
    )

    # Filter by relevance threshold
    relevant = [c for c in chunks if c.get("distance", 1.0) < MAX_DISTANCE]

    if not relevant:
        return base_prompt, []

    # Build augmented prompt
    context_block = format_context_block(relevant)
    augmented = f"""{base_prompt}

{context_block}

IMPORTANT: When your answer draws from the retrieved context above, mention the source title naturally in your response (e.g. "According to All About Circuits..." or "Per the NEC..."). If the context doesn't cover the question, rely on your training knowledge and say so.
"""
    return augmented, relevant


def get_cited_sources(chunks: list[dict]) -> list[dict]:
    """Extract unique source citations from retrieved chunks."""
    seen = set()
    sources = []
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        title = meta.get("title", "")
        if title and title not in seen:
            seen.add(title)
            sources.append({
                "title": title,
                "domain": meta.get("domain", ""),
                "url": meta.get("url", ""),
                "type": meta.get("type", ""),
            })
    return sources
