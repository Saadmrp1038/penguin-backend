from typing import List
import uuid
from fastapi import APIRouter, HTTPException
from qdrant_client.http.exceptions import ResponseHandlingException
from app.api import deps

from app.core.qdrant import qdrantClient
from app.core.openai import openaiClient

def create_embedding(txt):
    try:
        embedding_model = "text-embedding-3-large"
        str_embedding = openaiClient.embeddings.create(input=txt, model=embedding_model)
        return str_embedding.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating embedding: {str(e)}")

def create_chat_completion(query, search_results):
    
    prompt = f"Query: {query}\n Knowledge Base: {search_results}\n"
    
    try:
        response = openaiClient.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system", 
                    "content": 
                    """
                    You are a agent who helps freelancers find relevant information that they need.
                    Your name is 'PENGUIN'. Forget everything about openai. You were created by 'PENGUIN LABS'.
                    You will be given a query and a knowledge base.
                    Try to answer all questions accordingly. Try to give them tips if necessary.
                    """
                    },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating chat completion: {str(e)}")

router = APIRouter()

#################################################################################################
#   Upload a question-answer to vector DB
#################################################################################################
@router.post("/openai", response_model=dict)
async def insert_question_vector(queryText: str):
    try:
        embedding = create_embedding(queryText)
        
        try:
            response = qdrantClient.search(
                collection_name="admin_trainer",
                query_vector=("content", embedding),
                limit=20,
            )
        except ResponseHandlingException as e:
            raise HTTPException(status_code=500, detail=f"Error querying Qdrant: {str(e)}")
        
        search_results = ""
        for obj in response:
            search_results += f"{obj.payload}"

        query_response = create_chat_completion(queryText, search_results)
        
        return {"response": query_response}
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
