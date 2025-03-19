from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

# Import your functions from other modules
from ingest import ingest_directory
from retrieve import get_answer_from_docs
from memory import ConversationMemory
from pymilvus import connections

app = FastAPI(title="Chat with PDF", description="RAG application for PDF documents")
memory = ConversationMemory()
connections.connect("default", host="standalone", port="19530")

# Request models
class IngestRequest(BaseModel):
    file_path: str
    is_directory: bool = False
    collection_name: str = None
    semantic_chunking: bool = True

class QuestionRequest(BaseModel):
    question: str
    collection_name: str = None
    llm_model: str = "gemini-2.0-flash"
    
# API endpoints
@app.post("/ingest")
async def ingest_endpoint(request: IngestRequest):
    try:
        if request.is_directory:
            collection_name, file_count, total_chunks = ingest_directory(request.file_path, request.collection_name, request.semantic_chunking)
            return {
                "status": "success",
                "message": "Documents ingested to Milvus Database successfully",
                "data": {
                    "collection_name": collection_name,
                    "documents_processed": file_count,
                    "total_chunks": total_chunks
                }
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_endpoint(request: QuestionRequest):
    try:
        conversation_history = memory.get_history()
        print('conversation_history: ', conversation_history)
        answer, top_5_chunks = get_answer_from_docs(
            request.question, request.collection_name, conversation_history
        )
        memory.add_interaction(request.question, answer)
        
        return {
            "question": request.question,
            "answer": answer,
            "top_5_chunks": top_5_chunks,
            "history": conversation_history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear_memory():
    memory.clear()
    return {
        "status": "success", 
        "message": "Conversation memory cleared",
        "history": memory.get_history()
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7777, reload=True)