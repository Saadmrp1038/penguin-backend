from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, subqueryload
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.api import deps
from app.schemas.chats import Chat, ChatCreate, ChatUpdate, ChatWithMessages
from app.db.models.chats import Chat as ChatModel
from app.db.models.messages import Message as MessageModel
from app.helpers.openai_functions import rag_query

router = APIRouter()

#################################################################################################
#   CREATE CHAT
#################################################################################################
@router.post("/", response_model=Chat)
async def create_user(*, db: Session = Depends(deps.get_db), chat_in: ChatCreate):
    
    try:
        db_chat = ChatModel(
            user_id = chat_in.user_id,
            first_message = chat_in.first_message
        )
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        
        db_message = MessageModel(
            chat_id = db_chat.id,
            sender = "user",
            content = db_chat.first_message
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
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
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
    
#################################################################################################
#   GET ALL CHAT PREVIEWS FOR A USER BY USER ID
#################################################################################################
@router.get("/users/{user_id}", response_model=List[Chat])
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
            setattr(db_chat, key, value)

        db.commit()
        db.refresh(db_chat)
        return db_chat
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
#   GET ALL MESSAGES FOR A CHAT USING CHAT_ID
#################################################################################################
@router.get("/{chat_id}", response_model=ChatWithMessages)
async def get_chat_with_messages(*, db: Session = Depends(deps.get_db), chat_id: uuid.UUID):
    try:
        db_chat = (
            db.query(ChatModel)
            .options(subqueryload(ChatModel.messages).order_by(MessageModel.created_at))
            .filter(ChatModel.id == chat_id)
            .first()
        )
        if not db_chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return db_chat
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))