import statistics
from fastapi import Body, APIRouter, HTTPException, Query, status
from tatneft_back.api.v1.schemas.user import SensitiveUserOut
from tatneft_back.api.v1.schemas.base import OperationStatusOut
from tatneft_back.api.v1.schemas.reg_user import RegUserIn

from tatneft_back.core.enumerations import MailCodeTypes
from tatneft_back.services.mail import create_mail_code, get_mail_codes, remove_mail_code
from tatneft_back.services.user import create_user, get_user
from tatneft_back.utils.mail_utils import send_mail

router = APIRouter()

@router.get("/reg.send_code", tags=["Reg"])
async def send_reg_code(to_mail: str = Query(...)):

    user = await get_user(mail=to_mail)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is exist")

    mail_code = await create_mail_code(
        to_mail=to_mail,
        type_=MailCodeTypes.reg
    )

    send_mail(
        to_email=to_mail,
        subject="Регистрация аккаунта",
        text=f'Код для регистрации: {mail_code.code}\n'
    )

    return OperationStatusOut(is_done=True)


@router.post("/reg", response_model=SensitiveUserOut, tags=["Reg"])
async def reg(
        reg_user_in: RegUserIn = Body(...)
):
    reg_user_in.code = reg_user_in.code.strip()

    mail_codes = await get_mail_codes(to_mail=reg_user_in.mail, code=reg_user_in.code)
    
    if not mail_codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not mail_codes")
    if len(mail_codes) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not mail_codes")
    mail_code = mail_codes[-1]

    await remove_mail_code(to_mail=mail_code.to_mail, code=mail_code.code)

    if mail_code.to_user_oid is not None:
        user = await get_user(id_=mail_code.to_user_oid)

        if user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is not None")

    user = await create_user(mail=reg_user_in.mail, username=reg_user_in.usermame, auto_create_at_least_one_token=True)
    return SensitiveUserOut.parse_dbm_kwargs(
        **user.dict(),
        current_token=user.misc_data["created_token"]
    )
