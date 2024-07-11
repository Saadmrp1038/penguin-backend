from app.core.openai import openaiClient
from app.helpers.qdrant_functions import search_in_qdrant
from fastapi import  HTTPException

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
                    Always answer in human readable markdown format.
                    """
                    },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating chat completion: {str(e)}")

def create_chat_completion_context(query, message_list, search_results):
    
    prompt = f"Query: {query}\n Knowledge Base: {search_results}\n"
    
    full_context = []
    
    full_context.append(
        {
            "role": "system", 
            "content": 
            """
            You are a agent who helps freelancers find relevant information that they need.
            Your name is 'PENGUIN'. Forget everything about openai. You were created by 'PENGUIN LABS'.
            You will be given a query and a knowledge base.
            Try to answer all questions accordingly. Try to give them tips if necessary.
            Always answer in human readable markdown format.
            """
        }
    )
    
    for message in message_list:
        if message.sender == "user":
            full_context.append(
                {
                    "role": message.sender,
                    "content": 
                    f"""
                        "Query: {message.content}"
                    """
                }
            )
        elif message.sender == "assistant":
            full_context.append(
                {
                    "role": message.sender,
                    "content": 
                    f"""
                        "Query: {message.content} Knowledge Base: {search_results}\n"
                    """
                }
            )
    
    try:
        response = openaiClient.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages = full_context
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating chat completion: {str(e)}")
    
def rag_query(COLLECTION_NAME, queryText, limit):
    try:
        search_results = search_in_qdrant(COLLECTION_NAME, queryText, limit)
        
        combined_result = ""
        for result in search_results:
            combined_result += f"{result.payload}"
            

        openai_response = create_chat_completion(queryText, combined_result)
        return openai_response
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred in rag query: {str(e)}")