from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CardioGuard AI Wellness Engine",
    description="General Wellness & Lifestyle Monitoring Platform - Non-Medical Service",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the PWA domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "CardioGuard AI Brain is online", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
