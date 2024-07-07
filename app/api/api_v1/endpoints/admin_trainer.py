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


#################################################################################################
#   Helper function to get the chunks for any text
#   input: string, output: array of semantically similar chunks
#   used method: percentile -> default value for breakpoint = 95%
#################################################################################################
def create_semantic_chunks(text_content):
    semantic_chunker = SemanticChunker(OpenAIEmbeddings(model="text-embedding-3-large"), breakpoint_threshold_type="percentile")
    semantic_chunks = semantic_chunker.create_documents([text_content])
    return semantic_chunks

#################################################################################################
#   Helper function to get the vector embedding for any text
#   input: string, output: multidimensional array representing embedding
#################################################################################################
def create_embedding(txt):
    embedding_model = "text-embedding-3-large"
    str_embedding = openaiClient.embeddings.create(input= txt, model=embedding_model)
    return str_embedding.data[0].embedding

#################################################################################################
#   Helper function to generate the summary for a question - answer_chunk pair. The summary is then prepended
#   input: semantic chunks, output: array of strings
#################################################################################################
def generate_summary(semantic_chunks, question):  
    summaries = []  # New list to store summaries
    for semantic_chunk in semantic_chunks:   
        prompt = f"Question: {question}\nAnswer: {semantic_chunk.page_content}"
        prompt += "\nPlease provide a brief summary about this question and answer within 1 sentence."

        response = openaiClient.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
        ],
        )
        raw_response = response.choices[0].message.content
        summaries.append(raw_response)  # Store summary in the list
    
    return summaries  

#################################################################################################
#   Helper function to upload into qdrant cloud
#   input: question, semantic chunks, summaries and output: nothing
#################################################################################################
def upload_to_qdrant(question: Question, semantic_chunks, summaries, collection_name):
    embedding_model = "text-embedding-3-large"
    point_count = qdrantClient.count(collection_name)
    index = point_count.count
    summary_index = 0

    for semantic_chunk in semantic_chunks:
        # Create payload from Question object fields
        payload = {
            "id": str(question.id),
            "question": question.question,
            "answer": semantic_chunk.page_content,
            "url": question.url,
            "created_at": question.created_at.isoformat(),
            "updated_at": question.updated_at.isoformat()
        }

        if not payload['answer']:
            return

        str_to_embed = question.question + "\n" + summaries[summary_index] + "\n" + semantic_chunk.page_content
        content_embedding = openaiClient.embeddings.create(input=str_to_embed, model=embedding_model)

        qdrantClient.upsert(
            collection_name,
            points=[
                {
                    "id": index,
                    "vector": {
                        "content": content_embedding.data[0].embedding
                    },
                    "payload": payload
                }
            ]
        )
        index += 1
        summary_index += 1

#################################################################################################
#   Helper function to Get all the vector-point IDs for a particular UUID of a question
#   input: UUID and output: array of points
#################################################################################################
def get_points_by_uuid(collection_name, uuid):
    offset = None
    all_points = []
    
    while True:
        result = qdrantClient.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(key="id", match=models.MatchValue(value=uuid)),
                ]
            ),
            limit=20,  
            with_payload=False,
            with_vectors=False,
            offset=offset
        )
        
        points, next_offset = result
        all_points.extend(points)
        
        if next_offset is None:
            break
        
        offset = next_offset
    
    all_point_ids = []
    all_point_ids.extend([point.id for point in points])
    return all_point_ids


#################################################################################################
#   Helper function to DELETE all the vector-point IDs for a particular UUID of a question
#   input: UUID and output: array of points
#################################################################################################
def delete_points_by_uuid(collection_name, uuid):
    try:
        response = qdrantClient.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="id",
                            match=models.MatchValue(value=uuid),
                        ),
                    ],
                )
            ),
        )
        
        # print(response)
        return True
        
    
    except Exception as e:
        print(f"An error occurred while deleting points: {e}")
        return False



router = APIRouter()
#################################################################################################
#   Upload a question-answer to vector DB
#################################################################################################
@router.post("/vector_insert")
async def insert_question_vector(question: Question):
    if question.answer:
        semantic_chunks = create_semantic_chunks(question.answer)
        summaries = generate_summary(semantic_chunks, question)
        upload_to_qdrant(question, semantic_chunks, summaries, "admin_trainer")
        return {"detail": "Question added to vector DB successfully"}
    else:
        raise HTTPException(status_code=404, detail="Action could not be performed because answer is empty")



#################################################################################################
#   Update a question-answer in vector DB
#################################################################################################
@router.put("/put/{question_id}")
async def update_question_vector(question_id: str, question: Question):
    try:
        collection_name = "admin_trainer"
        
        
        delete_success = delete_points_by_uuid(collection_name, question_id)
        if not delete_success:
            raise HTTPException(status_code=500, detail="Failed to delete existing question from vector DB")
        
        
        if question.answer:
            semantic_chunks = create_semantic_chunks(question.answer)
            summaries = generate_summary(semantic_chunks, question.question)
            upload_to_qdrant(question, semantic_chunks, summaries, "admin_trainer")
            
            return {"detail": f"Question with ID {question.id} updated in vector DB successfully"}
        else:
            raise HTTPException(status_code=400, detail="Action could not be performed because answer is empty")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during update: {str(e)}")
    
    


#################################################################################################
#   Delete a question-answer from vector DB
#################################################################################################
@router.delete("/del/{question_id}")
async def delete_question_vector(question_id: str):
    try:
        collection_name = "admin_trainer"
        success = delete_points_by_uuid(collection_name, question_id)
        
        if success:
            return {"detail": f"Question with ID {question_id} deleted from vector DB successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete question from vector DB")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


