from fastapi import APIRouter
from apps.api.api.v1.conversations import router as conversations_router
from apps.api.api.v1.onboarding import router as onboarding_router
from apps.api.api.v1.auth import router as auth_router

router = APIRouter()

router.include_router(onboarding_router, prefix="/auth", tags=["auth"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
