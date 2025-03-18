from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

# Import your functions from other modules
from ingest import ingest_directory
from retrieve import get_answer_from_docs
# from app.memory import ConversationMemory

app = FastAPI(title="Chat with PDF", description="RAG application for PDF documents")

# Initialize conversation memory
# memory = ConversationMemory()

# Request models
class IngestRequest(BaseModel):
    file_path: str
    is_directory: bool = False

class QuestionRequest(BaseModel):
    question: str
    
# API endpoints
@app.post("/ingest")
async def ingest_endpoint(request: IngestRequest):
    try:
        if request.is_directory:
            collection_name, file_count, total_chunks = ingest_directory(request.file_path)
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
    """
    Ask a question about the ingested PDFs.
    """
    try:
        # Get conversation history from memory
        # conversation_history = memory.get_history()
        
        # Get answer using RAG
        answer = get_answer_from_docs(
            request.question
            # , 
            # conversation_history=conversation_history
        )
        
        # Save the Q&A to memory
        # memory.add_interaction(request.question, answer)
        
        return {
            "question": request.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear_memory():
    """
    Clear the conversation memory.
    """
    # memory.clear()
    return {"status": "success", "message": "Conversation memory cleared"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7777, reload=True)