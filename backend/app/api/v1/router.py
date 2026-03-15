from fastapi import APIRouter
from app.api.v1.endpoints import vitals

api_router = APIRouter()

# Include the vitals router
api_router.include_router(vitals.router, prefix="/vitals", tags=["Vitals & Neural Ingestion"])
