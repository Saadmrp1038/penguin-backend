from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.api import deps
from app.schemas.chats import Chat, ChatCreate, ChatUpdate
from app.db.models.chats import Chat as ChatModel

router = APIRouter()

#################################################################################################
#   CREATE CHAT
#################################################################################################
@router.post("/", response_model=Chat)
async def create_user(*, db: Session = Depends(deps.get_db), chat_in: ChatCreate):
    
    try:
        db_chat = ChatModel(
            user_id = chat_in.user_id,
            name = chat_in.name
        )
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
    
#################################################################################################
#   DELETE CHAT BY ID
#################################################################################################
@router.delete("/{chat_id}", response_model=dict)
async def delete_chat_by_id(*, db: Session = Depends(deps.get_db), chat_id: uuid.UUID):
    try:
        db_chat = db.query(ChatModel).filter(ChatModel.id == chat_id).first()
        if not db_chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        db.delete(db_chat)
        db.commit()
        
        return {"detail": "Chat deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
    
#################################################################################################
#   GET ALL CHAT PREVIEWS FOR A USER BY USER ID
#################################################################################################
@router.get("/users/{user_id}", response_model=List[ChatPreview])
async def get_chats_for_user(*, db: Session = Depends(deps.get_db), user_id: uuid.UUID):
    try:
        db_chats = db.query(ChatModel).filter(ChatModel.user_id == user_id).all()
        return db_chats
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   UPDATE CHAT BY ID
#################################################################################################
@router.put("/{chat_id}", response_model=Chat)
async def update_chat_by_id(*, db: Session = Depends(deps.get_db), chat_id: uuid.UUID, chat_in: ChatUpdate):
    try:
        db_chat = db.query(ChatModel).filter(ChatModel.id == chat_id).first()
        if not db_chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        update_data = chat_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(chat_in, key, value)

        db.commit()
        db.refresh(db_chat)
        return db_chat
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))