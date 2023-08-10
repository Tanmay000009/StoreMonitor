from fastapi import APIRouter
from . import sync

api_router = APIRouter()

api_router.include_router(sync.router, prefix="/sync", tags=["Sync"])
