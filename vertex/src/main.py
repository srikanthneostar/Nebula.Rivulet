from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from auth import create_access_token, verify_token
from services.chromaService import ChromaSearch
from services.faissService import FaissSearch
from services.ollamaSearchService import OllamaSearch
from fastapi import BackgroundTasks
from app import celery, get_api_task_status
from pipelines.journalEventsPipeline import JournalEventsPipeline
from services.searchService import SearchService

app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
    title="Nebula Rivulet",
    description="API for performing authenticated Elasticsearch searches",
    version="1.0.0",
    openapi_tags=[
        {"name": "authentication", "description": "Authentication operations"},
        {"name": "search", "description": "Search operations"},
    ],
)


class SearchQuery(BaseModel):
    query: Dict = Field(..., example={"query": {"match": {"field": "value"}}})
    size: Optional[int] = Field(1000, description="Number of results to return")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SearchRequest(BaseModel):
    query: str
    k: int
    llmsearch: bool


class ContextRequest(BaseModel):
    entityid: int
    ids: List[int]
    guid: str = None


class SearchResponse(BaseModel):
    guid: str
    query: str
    session_id: str = None



@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Rivulet is running..."}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {"status": "healthy"}


@app.post("/login", response_model=TokenResponse, tags=["authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get access token for API authentication.

    - **username**: Your username
    - **password**: Your password
    """
    if form_data.username == "admin" and form_data.password == "password":
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")


@app.post("/run_chroma_pipeline", tags=["search"])
async def run_chroma_pipeline(background_tasks: BackgroundTasks, current_user: str = Depends(verify_token)):
    """
    Run the Chroma pipeline.
    """
    try:
        background_tasks.add_task(JournalEventsPipeline().run)
        return {"message": "Chroma pipeline started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chroma pipeline failed: {str(e)}")


@app.post("/chroma/search", tags=["search"])
async def vertex_search(
    request: SearchRequest, current_user: str = Depends(verify_token)
):
    """
    Perform a search operation using Vertex Chroma Service.

    - **query**: The search query to be processed
    """
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        qry = ChromaSearch()
        results = qry.search_results(request.query, request.k, request.llmsearch)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chroma search failed: {str(e)}")


@app.post("/delete/id", tags=["search"])
async def delete_by_id(
    req_info: dict, current_user: str = Depends(verify_token)
) -> List[Dict]:
    """
    Delete a document by its ID.
    - **ids**: The list of IDs to be deleted
    """
    try:
        if not req_info:
            raise HTTPException(status_code=400, detail="ID cannot be empty")
        qry = ChromaSearch()
        ids = req_info["ids"]
        results = qry.delete_collection(ids)
        return [{"message": "Given ids are deleted"}] if results is None else results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Document deletion failed: {str(e)}"
        )


@app.post("/faiss/search", tags=["search"])
async def faiss_search(
    request: SearchRequest, current_user: str = Depends(verify_token)
) -> List[Dict]:
    """
    Perform a search operation using FAISS.
    - **query**: The search query to be processed
    """
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        qry = FaissSearch()
        results = qry.search_results(request.query)
        serialized_results = [
            result if isinstance(result, dict) else result.__dict__
            for result in results
        ]
        return serialized_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FAISS search failed: {str(e)}")


@app.post("/context/search", tags=["search"])
async def context_search(
    request: ContextRequest, current_user: str = Depends(verify_token)
) -> List[Dict]:
    try:
        if not request.entityid:
            raise HTTPException(status_code=400, detail="Entity ID cannot be empty")
        qry = OllamaSearch()
        results = qry.search_MongoDB(request.entityid, request.ids, request.guid)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context search failed: {str(e)}")


@app.post("/llm/search", tags=["search"])
async def llm_search(
    request: SearchResponse, current_user: str = Depends(verify_token)
):
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        qry = OllamaSearch()
        results = qry.search_Ollama(request.guid, request.query, request.session_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/knowledge/questions", tags=["search"])
async def get_knowledge_questions(current_user: str = Depends(verify_token)):
    try:
        ques = SearchService()
        questions = ques.get_questions()
        if not questions:
            raise HTTPException(
                status_code=404, detail="No questions found!!"
            )
        return questions

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get questions: {str(e)}"
        )


@app.post("/chat_history/session", tags=["search"])
async def get_session_chat_history(
    request: dict, current_user: str = Depends(verify_token)
):
    try:
        if not request["session_id"]:
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")
        chat = OllamaSearch()
        results = chat.get_session_chat(request["session_id"])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Session chat history retrieval failed: {str(e)}"
        )


@app.post("/detect/start/{task_name}")
async def run_detection(
    task_name: str, req: Request, background_tasks: BackgroundTasks
):
    req_info = await req.json()
    task = celery.send_task(task_name, args=[req_info])
    return {"message": "Task received 🔄", "task_id": task.id}


@app.get("/status/{task_id}")
def get_status(task_id):
    return JSONResponse(content=get_api_task_status(task_id))
