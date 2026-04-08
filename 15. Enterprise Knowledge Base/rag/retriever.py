"""
Retriever module for the Enterprise Knowledge Base RAG System.
Handles document retrieval from the Bedrock Knowledge Base.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from utils.aws_client import BedrockClient

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Represents a single retrieval result from the knowledge base."""
    document_id: str
    document_title: str
    content: str
    score: float
    source_uri: Optional[str]
    metadata: Dict[str, Any]
    chunk_index: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "document_id": self.document_id,
            "document_title": self.document_title,
            "content": self.content,
            "score": self.score,
            "source_uri": self.source_uri,
            "metadata": self.metadata,
            "chunk_index": self.chunk_index,
        }


class KnowledgeBaseRetriever:
    """Handles retrieval of relevant documents from the Bedrock Knowledge Base."""

    def __init__(self):
        """Initialize the retriever with AWS client."""
        self.client = BedrockClient()
        self.config = self.client.config
        logger.info("KnowledgeBaseRetriever initialized")

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        knowledge_base_id: Optional[str] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents from the knowledge base.

        Args:
            query: User's natural language query
            top_k: Number of results to retrieve (uses config if not provided)
            knowledge_base_id: Knowledge Base ID (uses config if not provided)

        Returns:
            List of RetrievalResult objects sorted by relevance score
        """
        logger.info(f"Starting retrieval for query: '{query}'")

        try:
            # Query the knowledge base
            response = self.client.query_knowledge_base(
                query=query,
                knowledge_base_id=knowledge_base_id,
                top_k=top_k
            )

            # Parse results
            results = self._parse_retrieval_response(response)
            logger.info(f"Retrieved {len(results)} relevant documents")

            return results

        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            raise

    def _parse_retrieval_response(self, response: dict) -> List[RetrievalResult]:
        """
        Parse the Bedrock Knowledge Base response into structured results.

        Args:
            response: Raw response from Bedrock retrieve API

        Returns:
            List of RetrievalResult objects
        """
        results = []
        results_list = response.get("retrievalResults", [])

        for idx, result in enumerate(results_list):
            try:
                # Extract content from result
                content = result.get("content", {}).get("text", "")

                # Extract metadata
                metadata = result.get("metadata", {})
                score = result.get("score", 0.0)

                # Build RetrievalResult
                retrieval_result = RetrievalResult(
                    document_id=metadata.get("documentId", f"doc_{idx}"),
                    document_title=metadata.get("title", metadata.get("x-amz-bedrock-kb-title", "Unknown")),
                    content=content,
                    score=score,
                    source_uri=metadata.get("uri", metadata.get("location", {}).get("s3Location", {}).get("uri", None)),
                    metadata=metadata,
                    chunk_index=idx
                )
                results.append(retrieval_result)

            except Exception as e:
                logger.warning(f"Error parsing result {idx}: {e}")
                continue

        # Sort by score (descending) to get highest relevance first
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def format_context_string(self, results: List[RetrievalResult]) -> str:
        """
        Format retrieval results into a context string for the LLM.

        Args:
            results: List of RetrievalResult objects

        Returns:
            Formatted context string with document markers
        """
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Document {i} - Score: {result.score:.2f}]\n"
                f"Title: {result.document_title}\n"
                f"Content:\n{result.content}\n"
                f"{'-' * 50}\n"
            )

        return "\n".join(context_parts)

    def get_citation_list(self, results: List[RetrievalResult]) -> List[Dict[str, Any]]:
        """
        Generate a list of citations from retrieval results.

        Args:
            results: List of RetrievalResult objects

        Returns:
            List of citation dictionaries with source information
        """
        citations = []
        seen_sources = set()

        for result in results:
            source = result.source_uri or result.document_id
            if source not in seen_sources:
                seen_sources.add(source)
                citations.append({
                    "index": len(citations) + 1,
                    "title": result.document_title,
                    "source": source,
                    "document_id": result.document_id,
                })

        return citations

    def clear_cache(self) -> None:
        """Clear any cached data (if implemented in future)."""
        logger.debug("Cache cleared")


def get_retriever() -> KnowledgeBaseRetriever:
    """Factory function to get a retriever instance."""
    return KnowledgeBaseRetriever()
