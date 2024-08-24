from pathlib import Path
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from tatneft_ai.utils_hack_tatneft.entity.MFiLkO import MFiLkO
from tatneft_ai.utils_hack_tatneft.video_cut_mp3 import video2audio
from tatneft_back.api.v1.schemas.event import EventOut, SensitiveEventOut
from tatneft_back.core.consts import db

from tatneft_back.api.v1.schemas.user import SensitiveUserOut
from tatneft_back.core.enumerations import UserRoles
from tatneft_back.core.settings import STATIC_DIRPATH
from tatneft_back.db.collections.user import UserFields
from tatneft_back.deps.user_deps import get_strict_current_user
from tatneft_back.models.user import User
from tatneft_back.services.event import get_event, get_events, get_my_events, upload_event
from tatneft_back.services.mail import create_mail_code, get_mail_codes, remove_mail_code
from tatneft_back.services.token import generate_token
from tatneft_back.services.user import get_user, update_user
from tatneft_back.utils.mail_utils import send_mail

router = APIRouter()


@router.post('/event.create', response_model=Optional[SensitiveEventOut], tags=['Event'])
async def create_event(
    request: Request,
    user: User = Depends(get_strict_current_user),
    uploaded_res: Optional[UploadFile] = File(None),
    privacy: Optional[str] = Form(...),
):
    if user.count_attemps < 1 and not(user.roles[0] == UserRoles.subscribed_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not enough count attemps")

    filename = None
    if uploaded_res is not None:
        filename: str = str(uuid4())
        type_: str = uploaded_res.filename.split('.')[-1].strip()
        if type_:
            filename += '.' + type_

        path = Path(STATIC_DIRPATH).joinpath(filename)
        with open(path, mode='wb') as f:
            f.write(await uploaded_res.read())
    
    event = await upload_event(filename=filename, user_id=user.int_id, privacy=privacy)
    
    video_path = f"{STATIC_DIRPATH}/{filename}"
    audio_path = f"{STATIC_DIRPATH}/{filename.split('.')[0].strip()}.mp3"
    
    video2audio(mp3=audio_path, mp4=video_path)
    a = MFiLkO(path_audio=audio_path, path_video=video_path)
    await a.run(sync_mode=True)

    if not(user.roles[0] == UserRoles.subscribed_user):
        await update_user(id_=user.oid, count=1)

    return SensitiveEventOut.parse_dbm_kwargs(
        **event.dict()
    )




@router.get('/event.all', response_model=list[EventOut], tags=['Event'])
async def get_all_events(
    user: User = Depends(get_strict_current_user),
    st: Optional[int] = Query(default=0), count: Optional[int] = Query(default=10)
    ):
    
    count_docs = await db.event_collection.count_documents()
    if st + 1 > count_docs or st < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="wrong pagination params")

    if st + count + 1 > count_docs:
        count = count_docs - st
    
    return [EventOut.parse_dbm_kwargs(**event.dict()) for event in await get_events()][st: st + count: 1][::-1]

@router.get('/event.my', response_model=list[EventOut], tags=['Event'])
async def get_all_my_events(
    user: User = Depends(get_strict_current_user),
    ):
    return [EventOut.parse_dbm_kwargs(**event.dict()) for event in await get_my_events(user_id=user.int_id)][::-1]

@router.get('/event.by_id', response_model=Optional[EventOut], tags=['Event'])
async def get_event_by_int_id(
    int_id: int,
    user: User = Depends(get_strict_current_user)
):
    event = await get_event(int_id=int_id)
    if event is None:
        raise HTTPException(status_code=400, detail="event is none")
    return EventOut.parse_dbm_kwargs(**event.dict())

