from datetime import datetime, timezone
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.api import deps
from app.schemas.questions import Question, QuestionCreate, QuestionUpdate
from app.db.models.questions import Question as QuestionModel
from app.helpers.qdrant_functions import create_semantic_chunks, generate_summary, get_points_by_uuid, delete_points_by_uuid, upload_to_qdrant

router = APIRouter()

#################################################################################################
#   GET QUESTION BY ID
#################################################################################################
@router.get("/{question_id}", response_model=Question)
async def get_question_by_id(question_id: uuid.UUID, db: Session = Depends(deps.get_db)):
    try:
        db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if not db_question:
            raise HTTPException(status_code=404, detail="Question not found")
        return db_question
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

#################################################################################################
#   GET ALL QUESTIONS
#################################################################################################
@router.get("/", response_model=List[Question])
async def get_all_questions(db: Session = Depends(deps.get_db)):
    try:
        db_questions = db.query(QuestionModel).order_by(QuestionModel.updated_at.desc()).all()
        return db_questions
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   CREATE QUESTION
#################################################################################################
@router.post("/", response_model=Question)
async def create_question(*, db: Session = Depends(deps.get_db), question_in: QuestionCreate):
    
    try:
        db_question = QuestionModel(
            question=question_in.question,
            answer=question_in.answer,
            url=question_in.url,
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
#################################################################################################
#   UPDATE QUESTION BY ID
#################################################################################################
@router.put("/{question_id}", response_model=Question)
async def update_question_by_id(*, db: Session = Depends(deps.get_db), question_id: uuid.UUID, question_in: QuestionUpdate):
    try:
        db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if not db_question:
            raise HTTPException(status_code=404, detail="Question not found")

        update_data = question_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_question, key, value)

        db.commit()
        db.refresh(db_question)
        
        return db_question
    except HTTPException as http_exc:
        raise http_exc
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   DELETE QUESTION BY ID FROM DB AND QDRANT
#################################################################################################
@router.delete("/{question_id}", response_model=dict)
async def delete_question_by_id(*, db: Session = Depends(deps.get_db), question_id: uuid.UUID):
    try:
        db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if not db_question:
            raise HTTPException(status_code=404, detail="Question not found")

        db.delete(db_question)
        db.commit()
        
        try:
            collection_name = "admin_trainer"
            success = delete_points_by_uuid(collection_name, str(question_id))
            
            if success:
                return {"detail": f"Question with ID {question_id} deleted from DB & vectorDB successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to delete question from vectorDB")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while deleting from vectorDB: {str(e)}")
        
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
#################################################################################################
#   VECTORIZE QUESTION AND UPLOAD TO QDRANT
#################################################################################################
@router.get("/{question_id}/train", response_model=dict)
async def insert_question_vector(question_id: uuid.UUID, db: Session = Depends(deps.get_db)):
    try:
        collection_name = "admin_trainer"
        ids = get_points_by_uuid(collection_name, str(question_id))
        print(len(ids))
        if len(ids) != 0:
            success = delete_points_by_uuid(collection_name, str(question_id))
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to delete question from vectorDB")
        
        
        db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()

        if not db_question:
            raise HTTPException(status_code=404, detail="Question not found")

        if db_question.answer:
            semantic_chunks = create_semantic_chunks(db_question.answer)
            summaries = generate_summary(semantic_chunks, db_question)
            upload_to_qdrant(db_question, semantic_chunks, summaries, "admin_trainer")

            # Update the last_trained field
            db_question.last_trained = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_question)
            
            return {"detail": "Question added to vector DB successfully"}
        else:
            raise HTTPException(status_code=404, detail="Action could not be performed because answer is empty")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))