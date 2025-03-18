# Chat-with-PDF API

A powerful RAG (Retrieval-Augmented Generation) system that enables conversational interactions with PDF documents. This API service leverages Milvus for vector storage, LangChain for document processing, and supports multiple LLM providers including OpenAI and Google's Gemini.

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
   - PDF files are processed and split into manageable chunks
   - Each chunk is converted into a vector embedding using OpenAI's `text-embedding-3-large` model
   - Embeddings are stored in Milvus vector database with metadata

2. **Query Processing**:
   - User queries are converted to vector embeddings using the same model
   - Similar document chunks are retrieved from Milvus using vector similarity search
   - Retrieved context is sent to LLM along with the query
   - LLM (OpenAI or Gemini) generates a response based on the provided context

3. **Core Components**:
   - `main.py`: FastAPI application with endpoints for querying and document ingestion
   - `ingest.py`: Handles document processing and vector storage
   - `retrieve.py`: Manages similarity search and context retrieval
   - `memory.py`: Maintains conversation history for contextual responses

## Features

- **PDF Document Processing**: Automatically processes and indexes PDF documents
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

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/tanyaaton/chat-with-pdf-api.git
cd chat-with-pdf-api
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your-openai-api-key
GEMINI_KEY=your-gemini-api-key
```

### 3. Prepare Your PDF Documents

Add your PDF documents to the existing `papers` directory in the project root. This directory is already set up in the repository and mounted to the Docker container.:

```bash
# Copy your PDF files to the papers directory
cp /path/to/your/documents/*.pdf papers/
```

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

To process and index your PDF documents:

```bash
curl -X POST http://localhost:7777/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/papers", "is_directory": true}'
```

Note: Use the path `/app/papers` which is the mounted directory inside the container.

The API will return a response with the collection name, which you'll need for queries:

```json
{
  "status": "success",
  "message": "Documents ingested to Milvus Database successfully",
  "data": {
    "collection_name": "a1b2c3d4e5",
    "documents_processed": 5,
    "total_chunks": 120
  }
}
```

### 2. Ask Questions About Your Documents

Use the collection name from the previous step to ask questions:

```bash
curl -X POST http://localhost:7777/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics covered in these papers?", 
    "collection_name": "a1b2c3d4e5"
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
