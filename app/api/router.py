# app/api/router.py
from fastapi import APIRouter

from .message_api import router as message_router

router = APIRouter()
router.include_router(message_router)
