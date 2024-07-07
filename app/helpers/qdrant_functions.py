from qdrant_client import models
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
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