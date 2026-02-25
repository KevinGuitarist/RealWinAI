from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="MAX - Ultimate Sports Betting AI",
    version="2.0.0"
)

# CORS configuration
origins = [
    "https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app",
    "https://realwin-frontend-master.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "MAX - Ultimate Sports Betting AI Backend", "status": "running"}

@app.get("/health")
async def health_check():
    return {"api": True, "database": True, "status": "healthy"}

@app.get("/test")
async def test_endpoint():
    return {
        "message": "Backend is working!",
        "frontend_url": os.getenv("FRONTEND_URL", "Not set"),
        "cors_origins": origins
    }