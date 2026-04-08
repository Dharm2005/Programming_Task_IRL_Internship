# Sample Documents for Enterprise Knowledge Base

This directory contains sample documents that can be ingested into your Bedrock Knowledge Base.

## Document Structure

Each document should be in the following format:

```
Title: [Document Title]

Content:
[Your document content here]
```

## Sample Documents

### 1. Employee Handbook
**Purpose**: Company policies, benefits, and procedures
**Key Topics**:
- Remote work policies
- Leave of absence
- Health benefits
- Code of conduct

### 2. Technical Documentation
**Purpose**: System architecture and technical specifications
**Key Topics**:
- API documentation
- Database schema
- Deployment processes
- Security protocols

### 3. Product Specifications
**Purpose**: Product features and capabilities
**Key Topics**:
- Feature descriptions
- Pricing models
- Integration guides
- Support information

### 4. Financial Reports
**Purpose**: Quarterly and annual financial data
**Key Topics**:
- Revenue figures
- Expense breakdown
- Projections
- Budget allocations

## Ingestion Process

To add documents to your Knowledge Base:

1. Use the AWS Console or CLI
2. Navigate to Amazon Bedrock > Knowledge Bases
3. Select your Knowledge Base
4. Click "Add Document"
5. Upload your file (PDF, DOCX, TXT, etc.)

## Document Format Requirements

- Maximum file size: 10MB per file
- Supported formats: PDF, DOCX, TXT, HTML
- Maximum documents: 100 per Knowledge Base

## Best Practices

1. **Chunking**: Break large documents into logical sections
2. **Naming**: Use descriptive, unique file names
3. **Metadata**: Include relevant metadata (date, author, department)
4. **Versioning**: Update documents with version numbers
