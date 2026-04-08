"""
Main Streamlit application for the Enterprise Knowledge Base RAG System.

This is the user-facing interface where users can ask questions about
internal company documents and receive grounded answers with citations.
"""

import logging
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from rag.pipeline import get_rag_pipeline, process_query, RAGResponse
from rag.retriever import RetrievalResult
from utils.config import get_config, validate_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Enterprise Knowledge Base Q&A",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "config" not in st.session_state:
        st.session_state.config = get_config()

    if "pipeline" not in st.session_state:
        st.session_state.pipeline = get_rag_pipeline()

    if "recent_queries" not in st.session_state:
        st.session_state.recent_queries = []

    if "show_retrieved_docs" not in st.session_state:
        st.session_state.show_retrieved_docs = True


def display_header():
    """Display the application header."""
    st.title("🏢 Enterprise Knowledge Base")
    st.markdown("Ask questions about your internal company documents and get accurate, citation-backed answers.")

    # Show configuration info in a subtle way
    config = st.session_state.config
    st.caption(
        f"Model: {config.model_id.split('/')[-1]} | "
        f"KB ID: {config.knowledge_base_id[:12]}... | "
        f"Region: {config.aws_region}"
    )


def display_citations(citations: list, source_docs: list):
    """Display citations section."""
    if not citations:
        return

    with st.expander(f"📚 Citations ({len(citations)} source{'s' if len(citations) > 1 else ''})", expanded=False):
        for citation in citations:
            source = citation.get("source", "Unknown")
            # Extract just the filename from the source URI if it's a path
            display_source = source.split("/")[-1] if "/" in source else source
            st.markdown(f"""
                **[{citation['index']}] {citation.get('title', 'Untitled')}**

                Source: `{display_source}`
            """)


def display_source_documents(retrieved_docs: list):
    """Display the source documents that were used to generate the answer."""
    if not retrieved_docs:
        return

    with st.expander(f"📄 Source Documents ({len(retrieved_docs)} chunks)", expanded=False):
        for i, doc in enumerate(retrieved_docs, 1):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**Document {i}: {doc.document_title}**")
                    st.markdown(f"*Score: {doc.score:.3f}*")
                with col2:
                    st.markdown(f" `#{doc.chunk_index}`")

                st.code(doc.content, language="text")
                st.divider()


def display_response(response: RAGResponse):
    """Display the complete RAG response."""
    if not response.query:
        st.error(response.answer)
        return

    # Answer section
    st.markdown("### Answer")
    st.markdown(response.answer)

    # Metadata and citations
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Citations"):
            if response.citations:
                for citation in response.citations:
                    source = citation.get("source", "Unknown")
                    display_source = source.split("/")[-1] if "/" in source else source
                    st.markdown(f"**[{citation['index']}] {citation.get('title', 'Untitled')}**")
                    st.markdown(f"*Source: `{display_source}`*")
                    st.markdown("---")
            else:
                st.info("No citations available")

    with col2:
        with st.expander("Source Documents"):
            if response.source_documents:
                for doc in response.source_documents[:3]:  # Show top 3
                    st.markdown(f"**{doc.document_title}**")
                    st.markdown(f"*Score: {doc.score:.3f}*")
                    st.code(doc.content[:300] + "..." if len(doc.content) > 300 else doc.content, language="text")
            else:
                st.info("No source documents available")

    # Timing information in sidebar
    st.sidebar.markdown("### ⚡ Performance")
    st.sidebar.markdown(f"Retrieval: `{response.retrieval_time_ms:.0f}ms`")
    st.sidebar.markdown(f"Generation: `{response.generation_time_ms:.0f}ms`")
    st.sidebar.markdown(f"**Total: `{response.total_time_ms:.0f}ms`**")


def display_query_form():
    """Display the query input form."""
    with st.form("query_form", clear_on_submit=False):
        user_query = st.text_area(
            "Ask a question about your documents:",
            placeholder="e.g., What are our policies on remote work?",
            height=100,
            label_visibility="collapsed"
        )

        col1, col2 = st.columns([4, 1])
        with col1:
            submitted = st.form_submit_button("🚀 Ask Question", type="primary")
        with col2:
            clear = st.form_submit_button("🗑️ Clear")

        if clear:
            st.session_state.last_query = ""
            st.session_state.last_response = None
            st.rerun()

        if submitted and user_query:
            return user_query

    return None


def display_status_bar():
    """Display status and configuration information in sidebar."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        config = st.session_state.config

        st.subheader("AWS Settings")
        st.code(f"Region: {config.aws_region}", language="text")
        st.code(f"Access Key: {config.aws_access_key[:4]}***" if config.aws_access_key else "Using default credentials", language="text")

        st.subheader("Bedrock Settings")
        st.code(f"Model: {config.model_id}", language="text")
        st.code(f"KB ID: {config.knowledge_base_id}", language="text")

        st.subheader("Pipeline Settings")
        st.code(f"Top-K: {config.top_k}", language="text")
        st.code(f"Temperature: {config.temperature}", language="text")
        st.code(f"Max Tokens: {config.max_tokens}", language="text")

        st.divider()

        # Cache info
        cache_info = st.session_state.pipeline.get_cache_info()
        st.subheader("Cache Status")
        st.code(f"Size: {cache_info['cache_size']}", language="text")
        if st.button("Clear Cache"):
            st.session_state.pipeline.clear_cache()
            st.success("Cache cleared!")
            st.rerun()


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # Display header
    display_header()

    # Display sidebar configuration
    display_status_bar()

    # Display query form
    user_query = display_query_form()

    # Process query if submitted
    if user_query:
        with st.spinner("🔍 Retrieving relevant documents..."):
            try:
                response = process_query(
                    query=user_query,
                    top_k=st.session_state.config.top_k
                )
                st.session_state.last_response = response
                st.session_state.last_query = user_query

                # Display response
                st.success(f"Processed in {response.total_time_ms:.0f}ms")
                display_response(response)

                # Add to recent queries
                if user_query not in st.session_state.recent_queries:
                    st.session_state.recent_queries.append(user_query)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Error processing query: {e}")
    elif st.session_state.get("last_response"):
        # Re-display previous response if it exists
        display_response(st.session_state.last_response)

    # Recent queries history
    if st.session_state.recent_queries:
        with st.expander("Recent Questions", expanded=False):
            for query in st.session_state.recent_queries[-5:]:
                st.markdown(f"- {query}")

    # Display footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Enterprise Knowledge Base Q&A System |Powered by Amazon Bedrock"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
