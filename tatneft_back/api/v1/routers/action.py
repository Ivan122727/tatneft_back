from pathlib import Path
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from tatneft_back.api.v1.schemas.action import ActionOut, SensitiveActionOut
from tatneft_back.api.v1.schemas.detected_human import DetectedHumanOut, SensitiveDetectedHumanOut
from tatneft_back.api.v1.schemas.event import EventOut, SensitiveEventOut
from tatneft_back.core.consts import db

from tatneft_back.api.v1.schemas.user import SensitiveUserOut
from tatneft_back.core.enumerations import UserRoles
from tatneft_back.core.settings import STATIC_DIRPATH
from tatneft_back.db.collections.user import UserFields
from tatneft_back.deps.user_deps import get_strict_current_user
from tatneft_back.models.user import User
from tatneft_back.services.action import create_action, get_action, get_actions
from tatneft_back.services.detected_human import create_detected_human, get_detected_human, get_detected_humans
from tatneft_back.services.event import get_event
from tatneft_back.services.user import get_user, update_user
from tatneft_back.utils.mail_utils import send_mail

router = APIRouter()

@router.post('/action.create', response_model=Optional[SensitiveActionOut], tags=['Action'])
async def upload_action(
    user: User = Depends(get_strict_current_user),
    detected_human_id: Optional[int] = Form(...),
    price: Optional[int] = Form(...),
    title: Optional[str] = Form(...),
    timeline: Optional[str] = Form(...),
    event_id: Optional[int] = Form(...),
):
    event = await get_event(int_id=event_id)
    if event is None:
        raise HTTPException(status_code=400, detail="event is none")
    
    detected_human = await get_detected_human(int_id=detected_human_id)
    if detected_human is None:
        raise HTTPException(status_code=400, detail="detected_human is none")
    
    action = await create_action(
        detected_human_id=detected_human_id, price=price,
        title=title, timeline=timeline,
        event_id=event_id
    )    

    return SensitiveActionOut.parse_dbm_kwargs(
        **action.dict()
    )

@router.get('/action.all', response_model=list[ActionOut], tags=['Action'])
async def get_all_actions(
    user: User = Depends(get_strict_current_user),
    event_id: Optional[int] = Query(...),
    ):
    event = await get_event(int_id=event_id)
    if event is None:
        raise HTTPException(status_code=400, detail="event is none")

    return [SensitiveActionOut.parse_dbm_kwargs(**action.dict()) for action in await get_actions(event_id=event_id)]


@router.get('/action.by_id', response_model=Optional[ActionOut], tags=['Action'])
async def get_action_by_int_id(
    int_id: int,
    user: User = Depends(get_strict_current_user)
):
    action = await get_action(int_id=int_id)
    if action is None:
        raise HTTPException(status_code=400, detail="action is none")
    return ActionOut.parse_dbm_kwargs(**action.dict())

