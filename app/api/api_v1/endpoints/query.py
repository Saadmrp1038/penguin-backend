from typing import List
import uuid
from fastapi import APIRouter, HTTPException
from qdrant_client.http.exceptions import ResponseHandlingException
from app.api import deps
from app.helpers.qdrant_functions import search_in_qdrant
from app.helpers.openai_functions import create_chat_completion

from app.core.qdrant import qdrantClient
from app.core.openai import openaiClient
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
        search_results = search_in_qdrant(COLLECTION_NAME, queryText, 20)
        
        combined_result = ""
        for result in search_results:
            combined_result += f"{result.payload}"
            

        openai_response = create_chat_completion(queryText, combined_result)
        
        query_response = Response(
            response = openai_response
        )
        # query_response = create_chat_completion(queryText, search_results)
        
        return query_response
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
