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
from app.schemas.issues import Issue, IssueCreate, IssueUpdate, IssueWithChat
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
#   UPDATE ISSUE
#################################################################################################
@router.put("/{issue_id}", response_model = Issue)
async def update_issue(*, db: Session = Depends(deps.get_db), issue_id: uuid.UUID, issue_in: IssueUpdate):
    
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
        
        # Serialize messages
        messages = [Message(
            id=msg.id,
            chat_id=msg.chat_id,
            sender=msg.sender,
            content=msg.content,
            knowledge=msg.knowledge,
            created_at=msg.created_at,
            updated_at=msg.updated_at
        ) for msg in db_chat.messages]

        # Create ChatWithMessages instance
        chat_with_messages = ChatWithMessages(
            id=db_chat.id,
            user_id=db_chat.user_id,
            first_message=db_chat.first_message,
            created_at=db_chat.created_at,
            updated_at=db_chat.updated_at,
            messages=messages
        )

        # Create IssueWithChat instance
        response = IssueWithChat(
            id=db_issue.id,
            user_id=db_issue.user_id,
            chat_id=db_issue.chat_id,
            message_id=db_issue.message_id,
            message_content=db_issue.message_content,
            feedback=db_issue.feedback,
            response=db_issue.response,
            status=db_issue.status,
            created_at=db_issue.created_at,
            updated_at=db_issue.updated_at,
            chat=chat_with_messages
        )
        
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
    