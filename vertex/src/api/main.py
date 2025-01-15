from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from database.elasticService import ElasticService

from auth import create_access_token, verify_token

class SearchQuery(BaseModel):
    query: Dict = Field(..., example={
        "query": {
            "match": {
                "field": "value"
            }
        }
    })
    size: Optional[int] = Field(1000, description="Number of results to return")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


app = FastAPI(
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

es_service = ElasticService(['http://localhost:9200'])


@app.post("/token", response_model=TokenResponse, tags=["authentication"])
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
        results = es_service.search(index, search_query.query, search_query.size)
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
