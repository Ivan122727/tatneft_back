from pathlib import Path
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from tatneft_back.api.v1.schemas.detected_human import DetectedHumanOut, SensitiveDetectedHumanOut
from tatneft_back.api.v1.schemas.event import EventOut, SensitiveEventOut
from tatneft_back.core.consts import db

from tatneft_back.api.v1.schemas.user import SensitiveUserOut
from tatneft_back.core.enumerations import UserRoles
from tatneft_back.core.settings import STATIC_DIRPATH
from tatneft_back.db.collections.user import UserFields
from tatneft_back.deps.user_deps import get_strict_current_user
from tatneft_back.models.user import User
from tatneft_back.services.detected_human import create_detected_human, get_detected_human, get_detected_humans
from tatneft_back.services.user import get_user, update_user
from tatneft_back.utils.mail_utils import send_mail

router = APIRouter()

@router.post('/detected_human.create', response_model=Optional[SensitiveDetectedHumanOut], tags=['DetectedHuman'])
async def upload_detected_human(
    request: Request,
    user: User = Depends(get_strict_current_user),
    uploaded_avatar: Optional[UploadFile] = File(None),
    usefulness: Optional[str] = Form(...),
):
    avatar_filename = None
    if uploaded_avatar is not None:
        avatar_filename: str = str(uuid4())
        type_: str = uploaded_avatar.filename.split('.')[-1].strip()
        if type_:
            avatar_filename += '.' + type_

        path = Path(STATIC_DIRPATH).joinpath(avatar_filename)
        with open(path, mode='wb') as f:
            f.write(await uploaded_avatar.read())
    
    detected_human = await create_detected_human(avatar_filename=avatar_filename, event_id=event_id, usefulness=usefulness)
    
    if not(user.roles[0] == UserRoles.subscribed_user):
        await update_user(id_=user.oid, count=1)

    return SensitiveEventOut.parse_dbm_kwargs(
        **detected_human.dict()
    )


@router.get('/detected_human.all', response_model=list[DetectedHumanOut], tags=['DetectedHuman'])
async def get_all_detected_humans(
    user: User = Depends(get_strict_current_user),
    st: Optional[int] = Query(default=0), count: Optional[int] = Query(default=10), event_id: Optional[int] = Query(...),
    ):
    
    count_docs = await db.detected_human_collection.count_documents()
    if st + 1 > count_docs or st < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="wrong pagination params")

    if st + count + 1 > count_docs:
        count = count_docs - st
    
    return [SensitiveDetectedHumanOut.parse_dbm_kwargs(**detected_human.dict()) for detected_human in await get_detected_humans(event_id=event_id)][st: st + count: 1]


@router.get('/detected_humans.by_id', response_model=Optional[DetectedHumanOut], tags=['DetectedHuman'])
async def get_detected_human_by_int_id(
    int_id: int,
    user: User = Depends(get_strict_current_user)
):
    detected_human = await get_detected_human(int_id=int_id)
    if detected_human is None:
        raise HTTPException(status_code=400, detail="detected_human is none")
    return DetectedHumanOut.parse_dbm_kwargs(**detected_human.dict())

