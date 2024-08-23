from fastapi import APIRouter

from tatneft_back.api.v1.routers import auth, detected_human, event, reg, user


api_v1_router = APIRouter()

api_v1_router.include_router(router=reg.router, prefix="/reg", tags=["Reg"])
api_v1_router.include_router(router=auth.router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(router=user.router, prefix="/user", tags=["User"])
api_v1_router.include_router(router=event.router, prefix="/event", tags=["Event"])
api_v1_router.include_router(router=detected_human.router, prefix="/detected_human", tags=["DetectedHuman"])