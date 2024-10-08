import httpx
from datetime import datetime, timezone
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.api import deps
from app.schemas.adminUrlTrain import webUrlTrain
from app.db.models.urlTrain import urltrain as urlModel
from app.helpers.qdrant_functions import create_semantic_chunks, generate_summary, get_points_by_uuid, delete_points_by_uuid, upload_to_qdrant

router = APIRouter()

COLLECTION_NAME = "admin_trainer"
local_path = "http://127.0.0.1:8001"
deploy_path = ""

#################################################################################################
#   GET Test
#################################################################################################
@router.get("/test")
async def test():
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.get("http://127.0.0.1:8001")
        return response.json()
    
#################################################################################################
#   GET Train info BY ID
#################################################################################################
@router.get("/id/{url_train_id}", response_model=webUrlTrain)
async def get_traininfo_by_id(url_train_id: uuid.UUID, db: Session = Depends(deps.get_db)):
    try:
        db_url = db.query(urlModel).filter(urlModel.id == url_train_id).first()
        if not db_url:
            raise HTTPException(status_code=404, detail="Train info not found with this URL ID")
        return db_url
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   GET ALL URL models
#################################################################################################
@router.get("/", response_model=List[webUrlTrain])
async def get_all_traininfo(db: Session = Depends(deps.get_db)):
    try:
        db_urls = db.query(urlModel).order_by(urlModel.scraped_at.desc()).all()
        return db_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   CREATE Train with URL
#################################################################################################
@router.post("/", response_model=webUrlTrain)
async def create_traininfo(url:str , db: Session = Depends(deps.get_db)):
    
    try:

        existing_url = db.query(urlModel).filter(urlModel.url == url).first()
        if existing_url:
            raise HTTPException(status_code=400, detail="URL already exists")
        db_url = urlModel(
            url = url
        )
        
        db.add(db_url)
        db.commit()
        db.refresh(db_url)

        secondary_backend_response = {}
        
        if len(db_url.url) > 0:
            async with httpx.AsyncClient(timeout=1000) as client:
                postUrl = local_path + "/api/v1/scrape/scrape/"
                payload = {"url": db_url.url, "id": str(db_url.id)}
                print(f"Sending payload to secondary backend: {payload}")
                response = await client.post(postUrl, json=payload)
                response.raise_for_status()
                secondary_backend_response = response.json()  # Assuming the response from the secondary backend is JSON
                print(f"Received response from secondary backend: {secondary_backend_response}")
        
        return webUrlTrain(
            id=db_url.id,
            url=db_url.url,
            scraped_at=datetime.now(timezone.utc)
        )

    
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except httpx.HTTPStatusError as http_exc:
        print(f"HTTP error from secondary backend: {http_exc.response.text}")
        raise HTTPException(status_code=http_exc.response.status_code, detail=f"Secondary backend error: {http_exc.response.text}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    

