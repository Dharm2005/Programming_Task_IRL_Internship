"""
Configuration module for the Enterprise Knowledge Base RAG System.
Handles environment variables and configuration management.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class AWSConfig:
    """AWS configuration settings."""
    region: str
    access_key: Optional[str]
    secret_key: Optional[str]
    session_token: Optional[str] = None


@dataclass
class BedrockConfig:
    """Bedrock-specific configuration."""
    knowledge_base_id: str
    model_id: str
    top_k: int
    temperature: float
    max_tokens: int
    timeout: int


@dataclass
class AppConfig:
    """Application-wide configuration."""
    # AWS Settings
    aws_region: str
    aws_access_key: Optional[str]
    aws_secret_key: Optional[str]

    # Bedrock Settings
    knowledge_base_id: str
    model_id: str

    # RAG Pipeline Settings
    top_k: int
    temperature: float
    max_tokens: int
    chunk_size: int
    chunk_overlap: int

    # Streamlit Settings
    app_title: str
    app_icon: str


def get_aws_credentials() -> dict:
    """Get AWS credentials from environment variables."""
    return {
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_session_token": os.getenv("AWS_SESSION_TOKEN"),
    }


def get_config() -> AppConfig:
    """Load and validate configuration from environment variables."""
    return AppConfig(
        # AWS Settings
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),

        # Bedrock Settings
        knowledge_base_id=os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "KB_PLACEHOLDER_ID"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),

        # RAG Pipeline Settings
        top_k=int(os.getenv("TOP_K", "5")),
        temperature=float(os.getenv("TEMPERATURE", "0.3")),
        max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),

        # Streamlit Settings
        app_title=os.getenv("APP_TITLE", "Enterprise Knowledge Base Q&A"),
        app_icon=os.getenv("APP_ICON", "🏢"),
    )


def validate_config(config: AppConfig) -> list[str]:
    """Validate configuration and return list of warnings."""
    warnings = []

    if config.knowledge_base_id == "KB_PLACEHOLDER_ID":
        warnings.append("BEDROCK_KNOWLEDGE_BASE_ID is not set. Please configure in .env file.")

    if not config.aws_access_key:
        warnings.append("AWS_ACCESS_KEY_ID not found. Using default credentials chain.")

    if not config.aws_secret_key:
        warnings.append("AWS_SECRET_ACCESS_KEY not found. Using default credentials chain.")

    return warnings
