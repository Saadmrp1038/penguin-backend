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