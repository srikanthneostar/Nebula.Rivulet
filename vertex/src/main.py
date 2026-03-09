from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from auth import create_access_token, verify_token
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
    description="API for performing authenticated MongoDB searches",
    version="1.0.0",
    openapi_tags=[
        {"name": "authentication", "description": "Authentication operations"},
        {"name": "search", "description": "Search operations"},
    ],
)


class SearchQuery(BaseModel):
    query: Dict = Field(..., example={"query": {"match": {"field": "value"}}})
    size: Optional[int] = Field(1000, description="Number of results to return")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ContextRequest(BaseModel):
    entityid: int
    ids: List[int]
    guid: str = None


class SearchResponse(BaseModel):
    guid: str
    query: str
    session_id: str = None


class UpdateOllamaURLRequest(BaseModel):
    url: str = Field(..., example="http://localhost:11434")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Rivulet is running..."}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {"status": "healthy"}


@app.post("/login", response_model=TokenResponse, tags=["authentication"])
async def login(request: LoginRequest):
    """
    Get access token for API authentication.
    """
    if request.username == "admin" and request.password == "password":
        access_token = create_access_token(data={"sub": request.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")


@app.post("/run_knowledge_questions", tags=["search"])
async def run_knowledge_pipeline(
    background_tasks: BackgroundTasks, current_user: str = Depends(verify_token)
):
    """
    Run the knowledge questions generation pipeline.
    """
    try:
        background_tasks.add_task(JournalEventsPipeline().run)
        return {"message": "Knowledge questions pipeline started"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Knowledge questions pipeline failed: {str(e)}"
        )


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
            raise HTTPException(status_code=404, detail="No questions found!!")
        return questions

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get questions: {str(e)}"
        )


@app.post("/update_ollama_url")
async def update_ollama_url(
    request: UpdateOllamaURLRequest, current_user: str = Depends(verify_token)
):
    try:
        if not request.url:
            raise HTTPException(status_code=400, detail="URL cannot be empty")
        url = OllamaSearch().update_ollama_url(request.url)
        return {"message": "Ollama URL updated successfully", "url": url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update Ollama URL: {str(e)}"
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
