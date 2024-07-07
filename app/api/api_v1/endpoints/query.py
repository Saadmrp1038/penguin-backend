from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from qdrant_client import models
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from app.api import deps
from app.schemas.questions import Question

from app.core.qdrant import qdrantClient
from app.core.openai import openaiClient

def create_embedding(txt):
    embedding_model = "text-embedding-3-large"
    str_embedding = openaiClient.embeddings.create(input= txt, model=embedding_model)
    return str_embedding.data[0].embedding

def create_chat_completion(query, search_results):
    prompt = f"Query: {query}\n\nSearch Results:\n"
    prompt += f"{search_results}"

    prompt += "\nPlease provide a detailed and humanized response to the query based on the search results above."
    response = openaiClient.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

router = APIRouter()
#################################################################################################
#   Upload a question-answer to vector DB
#################################################################################################
@router.post("/openai")
async def insert_question_vector(*, queryText: str):
    embedding = create_embedding(queryText)
    

    response = qdrantClient.search(
        collection_name="admin_trainer",
        query_vector=("content", embedding),
        limit=5,
    )   
    
    search_results = ""
    for obj in response:
        question = obj.payload['question']
        answer = obj.payload['answer']
        search_results += f"**Question:** {question}\n**Answer:** {answer}\n\n"

    query_reponse = create_chat_completion(queryText, search_results)
    
    print(query_reponse)
    return {"response": query_reponse}




