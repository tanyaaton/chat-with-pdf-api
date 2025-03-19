# Chat-with-PDF API

A powerful RAG (Retrieval-Augmented Generation) system that enables conversational interactions with PDF documents. This API service leverages Milvus for vector storage, LangChain for document processing, Azure Document Intelligence for document structure and layout, and supports Google's Gemini LLM.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

## Architecture Overview

This system follows a standard RAG (Retrieval-Augmented Generation) architecture:

1. **Document Ingestion Pipeline**:
   - PDF files are processed and split into manageable chunks using Azure Docment Intelligence
   - Each chunk is converted into a vector embedding using OpenAI's text-embedding-3-large model
   - Embeddings are stored in Milvus vector database with metadata

2. **Query Processing**:
   - User queries are converted to vector embeddings using the same model
   - Similar document chunks are retrieved from Milvus using vector similarity search
   - Retrieved context is sent to LLM along with the query and past conversation history
   - LLM (Gemini) generates a response based on the provided context

3. **Core Components**:
   - `main.py`: FastAPI application with endpoints for querying and document ingestion
   - `ingest.py`: Handles document processing and vector storage
   - `retrieve.py`: Manages similarity search and context retrieval
   - `memory.py`: Maintains conversation history for contextual responses

## Features

- **PDF Document Processing**: Automatically processes and indexes PDF documents
- **Semantic Chunking**: Option to use Azure Document Intelligence for more intelligent document chunking
- **Standard Text Splitting**: LangChain's RecursiveCharacterTextSplitter for basic document chunking
- **Vector Search**: Utilizes Milvus for efficient similarity search
- **Multiple LLM Support**: Compatible with both OpenAI and Google's Gemini models
- **Conversation Memory**: Maintains context across multiple queries
- **Docker Deployment**: Easy setup with Docker Compose
- **Web UI for Vector Database**: Milvus Attu for database monitoring and management

## Project Structure

```
chat-with-pdf-api/
│
├── app/                   # Main application code
│   ├── __init__.py
│   ├── ingest.py          # Document processing and vector storage
│   ├── main.py            # FastAPI application and endpoints
│   ├── memory.py          # Conversation context management
│   ├── retrieve.py        # Vector similarity search and LLM integration
│   └── __pycache__/
│
├── papers/                # PDF files for ingestion
│
├── volumes/               # Persistent data for containers
│   ├── etcd/              # ETCD data for Milvus
│   ├── milvus/            # Milvus vector database files
│   └── minio/             # MinIO object storage
│
├── .env                   # Environment variables
├── .gitignore
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # API service build configuration
├── requirements.txt       # Python dependencies
└── README.md
```

## Requirements

- Docker and Docker Compose
- OpenAI API key
- Google Gemini API key
- Azure Document Intelligence API key and endpoint (optional, for semantic chunking)

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/chat-with-pdf-api.git
cd chat-with-pdf-api
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your-openai-api-key
GEMINI_KEY=your-gemini-api-key
AZURE_DOC_KEY=your-azure-document-intelligence-key
AZURE_DOC_ENDPOINT=your-azure-document-intelligence-endpoint
```

The Azure Document Intelligence credentials are required only if you plan to use the semantic chunking feature.

### 3. Prepare Your PDF Documents

Add your PDF documents to the existing `papers` directory in the project root. This directory is already set up in the repository and mounted to the Docker container.

### 4. Start the Services

First, build the API container to ensure all dependencies are properly installed:

```bash
docker-compose build --no-cache api
```

Then launch all required services using Docker Compose:

```bash
docker-compose up -d
```

This will start the following containers:
- `milvus-etcd`: Configuration storage for Milvus
- `milvus-minio`: Object storage for Milvus
- `milvus-standalone`: Milvus vector database
- `milvus-attu`: Web UI for Milvus (accessible at http://localhost:8000)
- `rag_api`: The API service (accessible at http://localhost:7777)

### 5. Monitor the Setup

Check if all containers are running properly:

```bash
docker ps
```

## Usage

### 1. Ingest Documents

To process and index your PDF documents, the system provides two methods for splitting PDF documents into chunks:

#### 1.1 Standard Text Splitting

Uses LangChain's RecursiveCharacterTextSplitter to divide documents based on character count:
- Simple but effective for clean, well-formatted documents
- Configurable chunk size and overlap
- No additional API requirements

To use standard text splitting:

```bash
curl -X POST http://localhost:7777/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/papers", 
    "is_directory": true,
    "semantic_chunking": false
  }'
```

#### 1.2. Semantic Chunking (Default)

Uses Azure Document Intelligence to intelligently chunk documents based on their semantic structure:
- Maintains document structure (sections, headers, tables)
- Preserves relationships between content elements
- Better handles complex document layouts
- Requires Azure Document Intelligence API credentials

To use semantic chunking (default):

```bash
curl -X POST http://localhost:7777/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/papers", 
    "is_directory": true,
    "semantic_chunking": true
  }'
```

### 2. Ask Questions About Your Documents

Use the collection name from the previous step to ask questions:

```bash
curl -X POST http://localhost:7777/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics covered in these papers?", 
    "collection_name": "test_collection"
  }'
```

### 3. Clear Conversation History

To reset the conversation context:

```bash
curl -X POST http://localhost:7777/clear
```



## API Endpoints

- **POST /ingest**: Process and index PDF documents
  - Parameters:
    - `file_path`: String - Path to file or directory (use container paths)
    - `is_directory`: Boolean - Whether the path is a directory
    - `collection_name`: String (optional) - Custom name for the Milvus collection
    - `semantic_chunking`: Boolean (default: true) - Use Azure Document Intelligence for advanced document chunking

- **POST /ask**: Query your documents
  - Parameters:
    - `question`: String - Your question about the documents
    - `collection_name`: String - The Milvus collection name from ingestion

- **POST /clear**: Reset conversation history
  - No parameters required

## Troubleshooting

- **Container Path Issues**: When ingesting files, use paths inside the container (e.g., `/app/papers`) not local machine paths
- **Milvus Connection Errors**: Check if all Milvus-related containers are running properly
  - Verify with `docker logs milvus-standalone`
- **Azure Document Intelligence Errors**: 
  - Ensure your Azure credentials are correct in the .env file
  - Check if your Azure service has adequate quota for your document volume
- **API Errors**: Check the logs with `docker logs rag_api` for detailed error messages
- **Missing Embeddings**: Ensure your OpenAI API key has access to the embedding model
- **Gemini Errors**: Confirm your Gemini API key is valid and has proper permissions

## Future Improvements

1. **Enhanced Search Capabilities**:
   - Implement hybrid search combining vector similarity with keyword matching
   - Add metadata filtering options (date, author, etc.)
   - Optimize chunk size and overlap for better context retrieval

2. **Performance Optimizations**:
   - Implement response caching for frequent queries
   - Add batch processing for large document sets
   - Optimize embedding model selection for speed/quality tradeoffs

3. **Feature Additions**:
   - Support for more document types (DOCX, TXT, HTML)
   - Multi-user support with authentication
   - Document collection management interface
   - Streaming responses for better user experience
   - Document source tracking and citation

4. **UI Development**:
   - Web interface for document upload and chatting
   - Visualization for document similarity
   - Dashboard for system monitoring

5. **Deployment Improvements**:
   - Kubernetes configuration for scalable deployment
   - Monitoring and logging integrations
   - CI/CD pipeline setup

## License

[MIT License](LICENSE)
