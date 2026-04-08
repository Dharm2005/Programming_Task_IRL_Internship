# Enterprise Knowledge Base Q&A System

A Retrieval-Augmented Generation (RAG) application that allows users to ask natural language questions about internal company documents and receive accurate, citation-backed answers using Amazon Bedrock.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-orange.svg)
![AWS](https://img.shields.io/badge/Platform-AWS%20Bedrock-ff9900.svg)

## 🌟 Features

- **Semantic Search** - Retrieve relevant document chunks using Amazon Bedrock Knowledge Bases
- **Grounded Responses** - Generate answers strictly based on retrieved context
- **Citations** - All answers include source document references
- **Edge Case Handling** - Gracefully handles no relevant documents, ambiguous queries
- **Caching** - Caches repeated queries for faster responses
- **Production-Ready** - Modular code, logging, and error handling

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │ →  │   Retriever     │ →  │   Generator     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                            ↓
                                   ┌─────────────────┐
                                   │   Answer +      │
                                   │   Citations     │
                                   └─────────────────┘
```

## 📂 Project Structure

```
enterprise-rag-system/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── README.md             # This file
├── rag/
│   ├── retriever.py      # Knowledge base retrieval
│   ├── generator.py      # LLM-based answer generation
│   └── pipeline.py       # Unified RAG pipeline
├── utils/
│   ├── aws_client.py     # AWS Bedrock client
│   └── config.py         # Configuration management
└── data/                 # Sample documents (optional)
```

## 🔧 Setup Instructions

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

Set up AWS credentials using one of these methods:

**Option A: Environment Variables**
```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

**Option B: AWS CLI Configuration**
```bash
aws configure
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# AWS Settings
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
# AWS_SESSION_TOKEN=your_session_token  # Optional, if using temporary credentials

# Bedrock Settings
BEDROCK_KNOWLEDGE_BASE_ID=your_knowledge_base_id
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# RAG Pipeline Settings
TOP_K=5
TEMPERATURE=0.3
MAX_TOKENS=1024
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 5. Prepare Your Knowledge Base

Ensure you have:
- An existing Amazon Bedrock Knowledge Base
- Documents ingested into the Knowledge Base
- The Knowledge Base ID from step 1

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## 💡 Usage

1. Enter your question in the text area
2. Click "Ask Question"
3. View the generated answer with citations
4. Expand "Citations" or "Source Documents" to see the context

## 🛠️ Troubleshooting

### Common Issues

**"No relevant documents found"**
- Verify your Knowledge Base has documents ingested
- Try rephrasing your query
- Increase `TOP_K` value

**Authentication Errors**
- Verify AWS credentials are configured correctly
- Check that your IAM role has Bedrock permissions

**Model Invocation Errors**
- Ensure the model ID is correct and available in your region
- Check your account has Bedrock model access

## 🔐 Security Considerations

- Never commit `.env` files with credentials to version control
- Use IAM roles instead of access keys when possible
- Implement proper logging and monitoring in production
- Consider adding authentication for production deployments

## 📝 License

This project is provided as-is for educational and internal use.

## 👥 Contributing

Contributions are welcome! Please open an issue or submit a pull request.
