"""
RAG Pipeline module for the Enterprise Knowledge Base RAG System.
Combines retrieval and generation into a unified pipeline.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import time
import hashlib

from rag.retriever import KnowledgeBaseRetriever, RetrievalResult, get_retriever
from rag.generator import AnswerGenerator, GeneratedResponse, get_generator
from utils.config import get_config, validate_config

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class RAGRequest:
    """Represents a RAG pipeline request."""
    query: str
    top_k: int = 5
    knowledge_base_id: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    request_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RAGResponse:
    """Represents a complete RAG pipeline response."""
    request_id: str
    query: str
    answer: str
    citations: List[Dict[str, Any]]
    source_documents: List[RetrievalResult]
    retrieval_time_ms: float
    generation_time_ms: float
    total_time_ms: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request_id": self.request_id,
            "query": self.query,
            "answer": self.answer,
            "citations": self.citations,
            "source_documents": [r.to_dict() for r in self.source_documents],
            "retrieval_time_ms": self.retrieval_time_ms,
            "generation_time_ms": self.generation_time_ms,
            "total_time_ms": self.total_time_ms,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class RAGPipeline:
    """
    Unified RAG pipeline that combines retrieval and generation.

    This class coordinates the flow from user query to final answer,
    including caching, logging, and error handling.
    """

    def __init__(self):
        """Initialize the RAG pipeline with retriever and generator."""
        self.config = get_config()
        self.retriever = get_retriever()
        self.generator = get_generator()

        # Initialize cache for repeated queries
        self._query_cache: Dict[str, RAGResponse] = {}

        logger.info("RAGPipeline initialized")
        logger.debug(f"Configuration: {self.config}")

    def process(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_cache: bool = True
    ) -> RAGResponse:
        """
        Process a user query through the complete RAG pipeline.

        Args:
            query: User's natural language question
            top_k: Number of documents to retrieve (uses config if not provided)
            use_cache: Whether to use cached results for repeated queries

        Returns:
            RAGResponse with answer, citations, and timing info
        """
        start_time = time.time()
        request_id = hashlib.md5(str(start_time).encode()).hexdigest()[:8]

        # Validate query
        if not query or not query.strip():
            return RAGResponse(
                request_id=request_id,
                query="",
                answer="Please provide a valid question.",
                citations=[],
                source_documents=[],
                retrieval_time_ms=0,
                generation_time_ms=0,
                total_time_ms=0,
                timestamp=datetime.now().isoformat(),
                metadata={"error": "Empty query"}
            )

        query = query.strip()

        # Check cache first
        if use_cache and query in self._query_cache:
            logger.info(f"Cache hit for query: '{query}'")
            cached_response = self._query_cache[query]
            cached_response.metadata["cache_hit"] = True
            return cached_response

        # Initialize request object
        request = RAGRequest(
            query=query,
            top_k=top_k or self.config.top_k,
            knowledge_base_id=None
        )

        # Phase 1: Retrieval
        retrieval_start = time.time()
        logger.info(f"[{request_id}] Starting retrieval phase")
        try:
            retrieved_docs = self.retriever.retrieve(
                query=query,
                top_k=request.top_k,
                knowledge_base_id=request.knowledge_base_id
            )
            retrieval_time_ms = (time.time() - retrieval_start) * 1000
            logger.info(f"[{request_id}] Retrieval completed in {retrieval_time_ms:.2f}ms, found {len(retrieved_docs)} documents")
        except Exception as e:
            retrieval_time_ms = (time.time() - retrieval_start) * 1000
            logger.error(f"[{request_id}] Retrieval failed: {e}")
            return RAGResponse(
                request_id=request_id,
                query=query,
                answer=f"Error retrieving documents: {str(e)}",
                citations=[],
                source_documents=[],
                retrieval_time_ms=retrieval_time_ms,
                generation_time_ms=0,
                total_time_ms=0,
                timestamp=datetime.now().isoformat(),
                metadata={"error": f"Retrieval failed: {str(e)}"}
            )

        # Phase 2: Generate Answer
        generation_start = time.time()
        logger.info(f"[{request_id}] Starting generation phase")
        try:
            response = self.generator.generate_answer(
                query=query,
                retrieved_docs=retrieved_docs,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            generation_time_ms = (time.time() - generation_start) * 1000
            logger.info(f"[{request_id}] Generation completed in {generation_time_ms:.2f}ms")
        except Exception as e:
            generation_time_ms = (time.time() - generation_start) * 1000
            logger.error(f"[{request_id}] Generation failed: {e}")
            return RAGResponse(
                request_id=request_id,
                query=query,
                answer=f"Error generating answer: {str(e)}",
                citations=[],
                source_documents=retrieved_docs,
                retrieval_time_ms=retrieval_time_ms,
                generation_time_ms=generation_time_ms,
                total_time_ms=0,
                timestamp=datetime.now().isoformat(),
                metadata={"error": f"Generation failed: {str(e)}"}
            )

        # Calculate total time
        total_time_ms = (time.time() - start_time) * 1000

        # Build response
        rag_response = RAGResponse(
            request_id=request_id,
            query=query,
            answer=response.answer,
            citations=response.citations,
            source_documents=response.source_documents,
            retrieval_time_ms=retrieval_time_ms,
            generation_time_ms=generation_time_ms,
            total_time_ms=total_time_ms,
            timestamp=datetime.now().isoformat(),
            metadata={
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "cache_hit": False,
                "grounded": self.generator.check_grounding(response.answer, retrieved_docs),
            }
        )

        # Update cache
        if use_cache:
            self._query_cache[query] = rag_response
            # Limit cache size
            if len(self._query_cache) > 100:
                # Remove oldest entries
                oldest_keys = list(self._query_cache.keys())[:20]
                for key in oldest_keys:
                    del self._query_cache[key]

        return rag_response

    def process_with_logging(
        self,
        query: str,
        top_k: Optional[int] = None,
        verbose: bool = False
    ) -> RAGResponse:
        """
        Process a query with additional logging output.

        Args:
            query: User's question
            top_k: Number of documents to retrieve
            verbose: Whether to output detailed logs

        Returns:
            RAGResponse with answer and metadata
        """
        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        return self.process(query=query, top_k=top_k)

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state."""
        return {
            "cache_size": len(self._query_cache),
            "cache_keys": list(self._query_cache.keys())[:10],  # Show first 10
        }

    def clear_cache(self) -> None:
        """Clear the query cache."""
        self._query_cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "config": {
                "model_id": self.config.model_id,
                "knowledge_base_id": self.config.knowledge_base_id,
                "top_k": self.config.top_k,
            },
            "cache": self.get_cache_info(),
        }


# Global pipeline instance for easy access
_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create a global RAG pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


def process_query(
    query: str,
    top_k: Optional[int] = None,
    use_cache: bool = True
) -> RAGResponse:
    """
    Convenience function to process a query through the RAG pipeline.

    Args:
        query: User's question
        top_k: Number of documents to retrieve
        use_cache: Whether to use cached results

    Returns:
        RAGResponse with answer and metadata
    """
    pipeline = get_rag_pipeline()
    return pipeline.process(query=query, top_k=top_k, use_cache=use_cache)
