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

router = APIRouter()
#################################################################################################
#   Upload a question-answer to vector DB
#################################################################################################
@router.post("/vector_retrieval")
async def insert_question_vector(queryText: str):
    embedding = create_embedding(queryText)
    

    response = qdrantClient.search(
        collection_name="admin_trainer",
        query_vector=("content", embedding),
        limit=5,
    )   

    print(response[0].payload)
    return {"response": response[0].payload}




