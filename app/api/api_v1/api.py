from fastapi import APIRouter
from app.api.api_v1.endpoints import questions

api_router_v1 = APIRouter()

api_router_v1.include_router(questions.router, prefix="/questions", tags=["questions"])