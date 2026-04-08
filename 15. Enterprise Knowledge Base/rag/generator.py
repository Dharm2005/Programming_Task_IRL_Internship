"""
Generator module for the Enterprise Knowledge Base RAG System.
Handles LLM-based answer generation with grounding and citations.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from utils.aws_client import BedrockClient
from rag.retriever import RetrievalResult

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class GeneratedResponse:
    """Represents a generated answer with metadata."""
    answer: str
    citations: List[Dict[str, Any]]
    source_documents: List[RetrievalResult]
    prompt_tokens: int = 0
    completion_tokens: int = 0
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "answer": self.answer,
            "citations": self.citations,
            "source_documents": [r.to_dict() for r in self.source_documents],
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "generated_at": self.generated_at,
        }


class AnswerGenerator:
    """Handles LLM-based answer generation using retrieved context."""

    # System prompt that guides the model to use only provided context
    SYSTEM_PROMPT = """You are an intelligent assistant helping users answer questions based on internal company documents.

CRITICAL INSTRUCTIONS:
1. ONLY use the provided context documents to answer questions
2. If the answer cannot be found in the provided documents, state clearly: "I don't have enough information in the provided documents to answer this question."
3. Do not use external knowledge or make assumptions
4. Be precise and cite specific information from the documents
5. If multiple documents are relevant, reference them all appropriately
6. Keep answers concise but comprehensive
7. Always provide citations for your answers
"""

    def __init__(self):
        """Initialize the generator with AWS client."""
        self.client = BedrockClient()
        self.config = self.client.config
        logger.info("AnswerGenerator initialized")

    def generate_answer(
        self,
        query: str,
        retrieved_docs: List[RetrievalResult],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> GeneratedResponse:
        """
        Generate an answer using the retrieved documents as context.

        Args:
            query: User's question
            retrieved_docs: List of RetrievalResult objects from the knowledge base
            temperature: Temperature for generation (uses config if not provided)
            max_tokens: Maximum tokens to generate (uses config if not provided)

        Returns:
            GeneratedResponse with answer, citations, and source documents
        """
        logger.info(f"Generating answer for query: '{query}'")

        # Format context from retrieved documents
        context = self._format_context(retrieved_docs)

        # Build the prompt
        prompt = self._build_prompt(query, context)

        try:
            # Invoke the model
            response_text = self.client.invoke_model(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Generate citations from retrieved documents
            citations = self._generate_citations(retrieved_docs)

            # Create the response object
            response = GeneratedResponse(
                answer=response_text,
                citations=citations,
                source_documents=retrieved_docs
            )

            logger.info("Answer generated successfully")
            return response

        except Exception as e:
            logger.error(f"Error during answer generation: {e}")
            raise

    def _format_context(self, documents: List[RetrievalResult]) -> str:
        """
        Format documents into context for the LLM.

        Args:
            documents: List of RetrievalResult objects

        Returns:
            Formatted context string
        """
        if not documents:
            return "[No relevant documents found]"

        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[Document {i}]")
            context_parts.append(f"Title: {doc.document_title}")
            if doc.source_uri:
                context_parts.append(f"Source: {doc.source_uri}")
            context_parts.append(f"Content:\n{doc.content}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build the prompt for the LLM.

        Args:
            query: User's question
            context: Retrieved document context

        Returns:
            Formatted prompt string
        """
        prompt = f"""{self.SYSTEM_PROMPT}

User Question:
{query}

---
Context Documents:
{context}

---
Based on the context above, please answer the user's question. Include citations to specific documents.

Answer:
"""

        return prompt

    def _generate_citations(self, documents: List[RetrievalResult]) -> List[Dict[str, Any]]:
        """
        Generate citation information from retrieved documents.

        Args:
            documents: List of RetrievalResult objects

        Returns:
            List of citation dictionaries
        """
        citations = []
        seen_sources = set()

        for i, doc in enumerate(documents, 1):
            source = doc.source_uri or doc.document_id
            if source not in seen_sources:
                seen_sources.add(source)
                citations.append({
                    "index": i,
                    "title": doc.document_title,
                    "source": source,
                    "document_id": doc.document_id,
                    "content_snippet": doc.content[:150] + "..." if len(doc.content) > 150 else doc.content,
                })

        return citations

    def check_grounding(self, answer: str, documents: List[RetrievalResult]) -> bool:
        """
        Check if the answer is grounded in the provided documents.

        Args:
            answer: Generated answer text
            documents: Retrieved documents

        Returns:
            True if answer appears to be grounded, False otherwise
        """
        # Simple heuristic: check if answer contains content from documents
        answer_lower = answer.lower()
        doc_contents = " ".join(doc.content.lower() for doc in documents)

        # Check for key terms from documents in the answer
        words_in_context = set(word for word in doc_contents.split() if len(word) > 5)
        words_in_answer = set(word for word in answer_lower.split() if len(word) > 5)

        overlap = words_in_answer & words_in_context

        # If more than 10% of unique long words overlap, likely grounded
        if len(words_in_context) > 0:
            overlap_ratio = len(overlap) / len(words_in_context)
            return overlap_ratio > 0.10

        return True  # Default to passing if we can't calculate

    def handle_edge_cases(self, query: str, results: List[RetrievalResult]) -> Optional[str]:
        """
        Handle edge cases before answer generation.

        Args:
            query: User's question
            results: Retrieved documents

        Returns:
            Pre-response for edge cases, or None if normal generation should proceed
        """
        # Case 1: No relevant documents found
        if not results:
            return "I don't have enough information in the provided documents to answer this question. Please try rephrasing your question or explore other topics."

        # Case 2: All documents have very low relevance scores
        if results and all(r.score < 0.3 for r in results):
            return "The available documents don't seem to contain relevant information for this query. Try asking about a different topic or provide more specific details."

        return None  # Continue with normal generation


def get_generator() -> AnswerGenerator:
    """Factory function to get a generator instance."""
    return AnswerGenerator()
