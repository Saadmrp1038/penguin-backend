from fastapi import FastAPI, Request, Response, HTTPException
from app.api.api_v1.api import api_router_v1
from app.db import base  # Import base to register models
from fastapi.middleware.cors import CORSMiddleware
from app.core.supabase import supabase

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    if (
        request.method == "OPTIONS" 
        or request.url.path.startswith("/api/v1/questions")
        or request.url.path in [
            "/", 
            "/docs", 
            "/openapi.json",
            "/api/v1/auth/signin", 
            "/favicon.ico",
        ]
    ):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response("Unauthorized", status_code=401)

    token = auth_header.split(" ")[1]
    try:
        auth_response = supabase.auth.get_user(token)
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid user token")

        request.state.user_id = auth_response.user.id
    except Exception as e:
        print(f"Auth Error: {e}")
        return Response("Invalid user token", status_code=401)

    response = await call_next(request)
    return response

app.include_router(api_router_v1, prefix="/api/v1")

# Dummy Endpoint
@app.get("/")
async def get_question_by_id():
   return "Hello World"

# gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
