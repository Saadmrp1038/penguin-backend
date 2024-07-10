from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.api import deps

from app.db.models.issues import Issue as IssueModel
from app.db.models.chats import Chat as ChatModel

from app.schemas.chats import ChatWithMessages
from app.schemas.issues import Issue, IssueCreate, IssueUpdate, IssueWithChat, IssueUpdateClient
from app.schemas.messages import Message

router = APIRouter()

#################################################################################################
#   CREATE ISSUE
#################################################################################################
@router.post("/", response_model = Issue)
async def create_issue(*, db: Session = Depends(deps.get_db), issue_in: IssueCreate):
    
    try:
        db_issue = IssueModel(
            user_id = issue_in.user_id,
            chat_id = issue_in.chat_id,
            message_id = issue_in.message_id,
            message_content = issue_in.message_content,     
            feedback = issue_in.feedback,
            status = "open"
        )
        
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)
        
        return db_issue
    
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
#################################################################################################
#   UPDATE ISSUE FROM ADMIN SIDE
#################################################################################################
@router.put("/{issue_id}", response_model = Issue)
async def update_issue_from_admin(*, db: Session = Depends(deps.get_db), issue_id: uuid.UUID, issue_in: IssueUpdate):
    
    try:
        db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
        
        if not db_issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        update_data = issue_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_issue, key, value)

        db.commit()
        db.refresh(db_issue)
        
        return db_issue
    
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   UPDATE ISSUE FROM CLIENT SIDE
#################################################################################################
@router.put("/{issue_id}/user", response_model = Issue)
async def update_issue_from_client(*, db: Session = Depends(deps.get_db), issue_id: uuid.UUID, issue_in: IssueUpdateClient):
    
    try:
        db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
        
        if not db_issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        update_data = issue_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_issue, key, value)

        db.commit()
        db.refresh(db_issue)
        
        return db_issue
    
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   GET ISSUES ALONG WITH RELATED CHAT WITH ISSUE ID
#################################################################################################

@router.get("/{issue_id}/chat", response_model=IssueWithChat)
async def get_issue_with_chat(*, db: Session = Depends(deps.get_db), issue_id: uuid.UUID):
    try:
        db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
        
        if not db_issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        db_chat = (
            db.query(ChatModel)
            .options(joinedload(ChatModel.messages))
            .filter(ChatModel.id == db_issue.chat_id)
            .first()
        )
        if not db_chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Sort messages by created_at
        db_chat.messages.sort(key=lambda message: message.created_at)
        
        response = db_issue
        response.chat = db_chat
        
        # response = IssueWithChat.model_validate(db_issue)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   GET ALL ISSUES
#################################################################################################

@router.get("/", response_model=List[Issue])
async def get_all_issues(db: Session = Depends(deps.get_db)):
    try:
        db_issues = db.query(IssueModel).order_by(IssueModel.created_at.desc()).all()
        return db_issues
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    