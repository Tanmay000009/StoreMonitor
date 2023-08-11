from fastapi import APIRouter
from . import sync
from . import data

api_router = APIRouter()

api_router.include_router(sync.router, prefix="/sync", tags=["Sync"])
api_router.include_router(data.router, prefix="/data", tags=["Data"])
