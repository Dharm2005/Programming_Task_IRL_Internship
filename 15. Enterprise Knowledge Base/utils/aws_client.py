"""
AWS Client module for the Enterprise Knowledge Base RAG System.
Handles boto3 client initialization and AWS service connections.
"""

import logging
from typing import Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .config import get_config, get_aws_credentials

# Configure logging
logger = logging.getLogger(__name__)


class BedrockClient:
    """Manages AWS Bedrock client connections."""

    def __init__(self):
        """Initialize Bedrock clients with configured credentials."""
        self.config = get_config()
        self.aws_creds = get_aws_credentials()

        self.bedrock_runtime: Optional[object] = None
        self.bedrock_agent_runtime: Optional[object] = None
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Initialize Bedrock runtime and agent runtime clients."""
        try:
            # Create common kwargs for client initialization
            client_kwargs = {
                "region_name": self.config.aws_region,
            }

            # Add credentials if available
            if self.aws_creds.get("aws_access_key_id"):
                client_kwargs["aws_access_key_id"] = self.aws_creds["aws_access_key_id"]
            if self.aws_creds.get("aws_secret_access_key"):
                client_kwargs["aws_secret_access_key"] = self.aws_creds["aws_secret_access_key"]
            if self.aws_creds.get("aws_session_token"):
                client_kwargs["aws_session_token"] = self.aws_creds["aws_session_token"]

            # Initialize Bedrock Runtime client (for LLM inference)
            self.bedrock_runtime = boto3.client("bedrock-runtime", **client_kwargs)
            logger.info("Bedrock Runtime client initialized successfully")

            # Initialize Bedrock Agent Runtime client (for Knowledge Base operations)
            self.bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", **client_kwargs)
            logger.info("Bedrock Agent Runtime client initialized successfully")

        except BotoCoreError as e:
            logger.error(f"Failed to initialize Bedrock clients: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing Bedrock clients: {e}")
            raise

    def query_knowledge_base(
        self,
        query: str,
        knowledge_base_id: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> dict:
        """
        Query the Bedrock Knowledge Base for relevant documents.

        Args:
            query: The user's natural language query
            knowledge_base_id: Knowledge Base ID (uses config if not provided)
            top_k: Number of results to retrieve (uses config if not provided)

        Returns:
            Dictionary containing query results and metadata
        """
        kb_id = knowledge_base_id or self.config.knowledge_base_id
        top_k_value = top_k or self.config.top_k

        logger.info(f"Querying Knowledge Base '{kb_id}' with query: '{query}'")
        logger.debug(f"Retrieving top-{top_k_value} results")

        try:
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=kb_id,
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": top_k_value
                    }
                },
                retrievalQuery={"text": query}
            )
            return response

        except ClientError as e:
            logger.error(f"AWS ClientError during KB query: {e}")
            raise
        except BotoCoreError as e:
            logger.error(f"AWS BotoCoreError during KB query: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during KB query: {e}")
            raise

    def invoke_model(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Invoke a Bedrock LLM model to generate a response.

        Args:
            prompt: The prompt to send to the model
            model_id: Model ID to use (uses config if not provided)
            temperature: Temperature for generation (uses config if not provided)
            max_tokens: Maximum tokens to generate (uses config if not provided)

        Returns:
            Generated response text from the model
        """
        model_id = model_id or self.config.model_id
        temperature = temperature or self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        logger.info(f"Invoking model '{model_id}'")
        logger.debug(f"Parameters: temperature={temperature}, max_tokens={max_tokens}")

        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=self._build_invoke_body(prompt, temperature, max_tokens)
            )

            # Parse and return the response
            response_body = response["body"].read().decode("utf-8")
            return self._extract_response_text(response_body, model_id)

        except ClientError as e:
            logger.error(f"AWS ClientError during model invocation: {e}")
            raise
        except BotoCoreError as e:
            logger.error(f"AWS BotoCoreError during model invocation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during model invocation: {e}")
            raise

    def _build_invoke_body(self, prompt: str, temperature: float, max_tokens: int) -> dict:
        """
        Build the request body for Bedrock model invocation.

        Args:
            prompt: The prompt text
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary formatted for Bedrock API
        """
        # Different models have different request formats
        if "anthropic" in self.config.model_id.lower():
            # Claude model format
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ]
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        elif "amazon" in self.config.model_id.lower():
            # Amazon Titan format
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "temperature": temperature,
                    "maxTokenCount": max_tokens
                }
            }
        elif "meta" in self.config.model_id.lower():
            # Meta Llama format
            return {
                "prompt": prompt,
                "temperature": temperature,
                "max_gen_len": max_tokens
            }
        else:
            # Default generic format
            return {
                "inputText": prompt,
                "generationConfig": {
                    "temperature": temperature,
                    "maxTokenCount": max_tokens
                }
            }

    def _extract_response_text(self, response_body: str, model_id: str) -> str:
        """
        Extract response text from Bedrock model response.

        Args:
            response_body: Raw response from Bedrock
            model_id: Model that generated the response

        Returns:
            Extracted response text
        """
        import json

        try:
            response_dict = json.loads(response_body)

            if "anthropic" in model_id.lower():
                return response_dict.get("content", [{}])[0].get("text", "")
            elif "amazon" in model_id.lower():
                return response_dict.get("results", [{}])[0].get("outputText", "")
            elif "meta" in model_id.lower():
                return response_dict.get("generation", "")
            else:
                # Fallback for unknown formats
                return response_dict.get("outputText", "")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response JSON: {e}")
            return response_body
