"""
Enterprise Knowledge Base RAG System

A Retrieval-Augmented Generation application using Amazon Bedrock for
enterprise document search and question answering.
"""

__version__ = "1.0.0"
__author__ = "Dharm2005"

from .rag.pipeline import get_rag_pipeline, process_query

__all__ = [
    "get_rag_pipeline",
    "process_query",
]
