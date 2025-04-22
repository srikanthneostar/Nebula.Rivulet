from asyncio import Lock
from threading import RLock
import json
import concurrent.futures
import uuid
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from database.elasticService import ElasticService
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
import socketio
from .auth import create_access_token, verify_token
from .services.vertexChromaService import ChromaSearch
from .services.vertexFaissService import FaissSearch
from .services.vertexOllamaSearch import OllamaSearch
from .services.vertexMLService import run_anomaly_task, emit_status, run_forecast_task
import os

app = FastAPI(
    middleware=[
        Middleware(CORSMiddleware, allow_origins=[
                   "*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    ],
    title="Elasticsearch Search API",
    description="API for performing authenticated Elasticsearch searches",
    version="1.0.0",
    openapi_tags=[{
        "name": "authentication",
        "description": "Authentication operations"
    }, {
        "name": "search",
        "description": "Search operations"
    }]
)

router = APIRouter()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

active_tasks = {}
task_lock = RLock()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


class SearchQuery(BaseModel):
    query: Dict = Field(..., example={
        "query": {
            "match": {
                "field": "value"
            }
        }
    })
    size: Optional[int] = Field(
        1000, description="Number of results to return")


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
    guid : str = None


class SearchResponse(BaseModel):
    guid: str
    query: str
    session_id : str = None

class DetectionRequest(BaseModel):
    query: str
    parameters: dict = None

class ForecastRequest(BaseModel):
    query: str
    parameters: dict = None
    future_days: int = 30




es_service = ElasticService(['http://localhost:9200'])


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
    raise HTTPException(
        status_code=400,
        detail="Incorrect username or password"
    )


@app.post("/search/{index}", tags=["search"])
async def search(
        index: str,
        search_query: SearchQuery,
        current_user: str = Depends(verify_token)
) -> List[Dict]:
    """
    Perform an Elasticsearch search operation.

    - **index**: The Elasticsearch index to search
    - **search_query**: The search query in Elasticsearch DSL format
    """
    try:
        results = es_service.search(
            index, search_query.query, search_query.size)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/search/{index}/scroll", tags=["search"])
async def search_scroll(
        index: str,
        search_query: SearchQuery,
        scroll_time: str = "5m",
        current_user: str = Depends(verify_token)
) -> List[Dict]:
    """
    Perform a scrolled Elasticsearch search for large result sets.

    - **index**: The Elasticsearch index to search
    - **search_query**: The search query in Elasticsearch DSL format
    - **scroll_time**: Scroll context duration (e.g. "5m" for 5 minutes)
    """
    try:
        results = es_service.search_with_scroll(
            index,
            search_query.query,
            scroll=scroll_time,
            size=search_query.size
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scroll search failed: {str(e)}"
        )


@app.post("/chroma/search", tags=["search"])
async def vertex_search(
    request: SearchRequest,

    current_user: str = Depends(verify_token)
):
    """
    Perform a search operation using Vertex Chroma Service.

    - **query**: The search query to be processed
    """
    try:
        if not request.query:
            raise HTTPException(
                status_code=400, detail="Query cannot be empty")
        qry = ChromaSearch()
        results = qry.search_results(
            request.query, request.k, request.llmsearch)
        # serialized_results = [
        #     result if isinstance(result, dict) else result.__dict__ for result in results
        # ]
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chroma search failed: {str(e)}"
        )


@app.post("/delete/id", tags=["search"])
async def delete_by_id(
    req_info: dict,
    current_user: str = Depends(verify_token)
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
            status_code=500,
            detail=f"Document deletion failed: {str(e)}"
        )


@app.post("/faiss/search", tags=["search"])
async def faiss_search(
    request: SearchRequest,
    current_user: str = Depends(verify_token)
) -> List[Dict]:
    """
    Perform a search operation using FAISS.
    - **query**: The search query to be processed
    """
    try:
        if not request.query:
            raise HTTPException(
                status_code=400, detail="Query cannot be empty")
        qry = FaissSearch()
        results = qry.search_results(request.query)
        serialized_results = [
            result if isinstance(result, dict) else result.__dict__ for result in results
        ]
        return serialized_results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"FAISS search failed: {str(e)}"
        )


@app.post("/context/search", tags=["search"])
async def context_search(
    request: ContextRequest,
    current_user: str = Depends(verify_token)
) -> List[Dict]:
    try:
        if not request.entityid:
            raise HTTPException(
                status_code=400, detail="Entity ID cannot be empty")
        qry = OllamaSearch()
        results = qry.search_ElasticSearch(request.entityid, request.ids, request.guid)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Context search failed: {str(e)}"
        )


@app.post("/llm/search", tags=["search"])
async def llm_search(
    request: SearchResponse,
    current_user: str = Depends(verify_token)
):
    try:
        if not request.query:
            raise HTTPException(
                status_code=400, detail="Query cannot be empty")
        qry = OllamaSearch()
        results = qry.search_Ollama(request.guid, request.query, request.session_id)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/knowledge/questions", tags=["search"])
async def get_knowledge_questions(
    request: dict,
    current_user: str = Depends(verify_token)
):
    try:
        if not request.get("config_path"):
            raise HTTPException(
                status_code=400, detail="Config path cannot be empty")

        root_path = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))).replace("\\vertex", "\\rivulet\\src\\knowledge")
        config_file_path = os.path.join(
            root_path, request["config_path"].replace(".json", "")+".json")

        with open(config_file_path, 'r') as f:
            config = json.load(f)

        if "questions" not in config[1]:
            raise HTTPException(
                status_code=404, detail="No questions found in config file")

        return config[1]["questions"]

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Config file not found"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format in config file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get questions: {str(e)}"
        )


@app.post("/chat_history/session", tags=["search"])
async def get_session_chat_history(
    request: dict,
    current_user: str = Depends(verify_token)
):
    try:
        if not request["session_id"]:
            raise HTTPException(
                status_code=400, detail="Session ID cannot be empty")
        chat = OllamaSearch()
        results = chat.get_session_chat(request["session_id"])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Session chat history retrieval failed: {str(e)}"
        )


@router.post("/anomaly/streaming/start")
async def start_detection(request: DetectionRequest):
    guid = str(uuid.uuid4())
    
    # Proper lock usage
    task_lock.acquire()
    try:
        active_tasks[guid] = {
            "stop_flag": False,
            "status": "started",
            "result": None,
            "error": None
        }
    finally:
        task_lock.release()
    
    executor.submit(run_anomaly_task, guid, request.query, request.parameters)
    return {"guid": guid}

@router.post("/anomaly/streaming/stop/{guid}")
async def stop_detection(guid: str):
    task_lock.acquire()
    try:
        task = active_tasks.get(guid)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task['status'] in ['completed', 'failed', 'stopped']:
            raise HTTPException(status_code=400, detail=f"Task already {task['status']}")
        task['stop_flag'] = True
        task['status'] = 'stopping'
    finally:
        task_lock.release()
    
    await emit_status(guid, 'stopping')
    return {"message": "Stop signal sent", "guid": guid}

@app.get("/ml/status/{guid}")
async def get_status(guid: str):
    with task_lock:
        task = active_tasks.get(guid)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {**task, "guid": guid}


@app.post("/forecast/streaming/start")
async def start_forecast(request: ForecastRequest):
    guid = str(uuid.uuid4())
    with task_lock:
        active_tasks[guid] = {
            "stop_flag": False,
            "status": "started",
            "result": None,
            "error": None
        }
    executor.submit(
        run_forecast_task,
        guid,
        request.query,
        request.parameters,
        request.future_days
    )
    return {"guid": guid}


@app.post("/forecast/streaming/stop/{guid}")
async def stop_forecast(guid: str):
    with task_lock:
        task = active_tasks.get(guid)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task['status'] in ['completed', 'failed', 'stopped']:
            raise HTTPException(status_code=400, detail=f"Task already {task['status']}")
        task['stop_flag'] = True
        task['status'] = 'stopping'
        await emit_status(guid, 'stopping')
    return {"message": "Stop signal sent", "guid": guid}


@router.post("/router/anomaly/streaming/start")
async def start_detection(request: DetectionRequest):
    guid = str(uuid.uuid4())
    with task_lock:
        active_tasks[guid] = {
            "stop_flag": False,
            "status": "started",
            "result": None,
            "error": None
        }
    executor.submit(run_anomaly_task, guid, request.query, request.parameters)
    return {"guid": guid}

@router.post("/router/anomaly/streaming/stop/{guid}")
async def stop_detection(guid: str):
    with task_lock:
        task = active_tasks.get(guid)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task['status'] in ['completed', 'failed', 'stopped']:
            raise HTTPException(status_code=400, detail=f"Task already {task['status']}")
        task['stop_flag'] = True
        task['status'] = 'stopping'
        await emit_status(guid, 'stopping')
    return {"message": "Stop signal sent", "guid": guid}

@router.get("router/ml/status/{guid}")
async def get_status(guid: str):
    with task_lock:
        task = active_tasks.get(guid)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {**task, "guid": guid}

app.include_router(router)