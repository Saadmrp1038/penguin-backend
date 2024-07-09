from typing import List
import uuid
from fastapi import APIRouter, HTTPException
from qdrant_client.http.exceptions import ResponseHandlingException
from app.api import deps
from app.helpers.openai_functions import rag_query

from app.schemas.query import Response, Query

COLLECTION_NAME = "admin_trainer"

router = APIRouter()

#################################################################################################
#   Upload a question-answer to vector DB
#################################################################################################
@router.post("/openai", response_model=Response)
async def query_openai(query_in: Query):
    try:
        queryText = query_in.query
        openai_response = rag_query(COLLECTION_NAME, queryText, 20)
        
        query_response = Response(
            response = openai_response
        )
        
        return query_response
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
