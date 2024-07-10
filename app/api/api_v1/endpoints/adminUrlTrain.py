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

#################################################################################################
#   GET Train info BY url
#################################################################################################
@router.get("/{url}", response_model=webUrlTrain)
async def get_traininfo_by_url(url: str, db: Session = Depends(deps.get_db)):
    try:
        db_url = db.query(urlModel).filter(urlModel.url == url).first()
        if not db_url:
            raise HTTPException(status_code=404, detail="URL not found")
        return db_url
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
#################################################################################################
#   GET Train info BY ID
#################################################################################################
@router.get("/{url_train_id}", response_model=webUrlTrain)
async def get_question_by_id(url_train_id: uuid.UUID, db: Session = Depends(deps.get_db)):
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
async def get_all_questions(db: Session = Depends(deps.get_db)):
    try:
        db_urls = db.query(urlModel).order_by(urlModel.scraped_at.desc()).all()
        return db_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   CREATE Train with URL
#################################################################################################
@router.post("/", response_model=webUrlTrain)
async def create_question(url:str , db: Session = Depends(deps.get_db)):
    
    try:
        db_url = urlModel(
            url = url
        )
        
        db.add(db_url)
        db.commit()
        db.refresh(db_url)
        
        if len(db_url.url) > 0:
            # semantic_chunks = create_semantic_chunks(db_question.answer)
            # summaries = generate_summary(semantic_chunks, db_question)
            # upload_to_qdrant(db_question, semantic_chunks, summaries, COLLECTION_NAME)
            print("2nd backend e pathaitesi")
        
        return db_url
    
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    

    