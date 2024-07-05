from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.api import deps
from app.schemas.questions import Question, QuestionCreate, QuestionUpdate
from app.db.models.questions import Question as QuestionModel

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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

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
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   DELETE QUESTION BY ID
#################################################################################################
@router.delete("/{question_id}", response_model=dict)
async def delete_question_by_id(*, db: Session = Depends(deps.get_db), question_id: uuid.UUID):
    try:
        db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if not db_question:
            raise HTTPException(status_code=404, detail="Question not found")

        db.delete(db_question)
        db.commit()
        
        return {"detail": "Question deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))