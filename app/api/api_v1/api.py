from fastapi import APIRouter
from app.api.api_v1.endpoints import questions, auth, protected, users, chats, admin_trainer

api_router_v1 = APIRouter()

api_router_v1.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router_v1.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router_v1.include_router(protected.router, prefix="/protected", tags=["protected"])
api_router_v1.include_router(users.router, prefix="/users", tags=["users"])
api_router_v1.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router_v1.include_router(admin_trainer.router, prefix="/admin_trainer", tags=["admin_trainer"])