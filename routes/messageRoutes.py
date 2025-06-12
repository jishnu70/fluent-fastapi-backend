from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
import json
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from sqlalchemy.future import select
from database import get_db
from core.authentication import get_current_user, get_user_by_username
from models.User import User
from schemas.PartnerSchema import PartnerInfoResponse
from core.encryption import decode_jwt_token
from schemas.MessageSchema import MessageCreate, MessageResponse
from core.chatHub import get_chatHub, ChatHub
from crud.MessageCrud import create_message, get_messages
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/partnerinfo", response_model=PartnerInfoResponse)
async def get_partner_info(partnerID: int,user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).filter_by(id=partnerID))
        partner = result.scalar_one_or_none()

        if partner is None:
            logger.error("Partner does not exist")
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail={"message":"Partner does not exist"}
            )
        return partner
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message":str(e)}
        )

@router.get("/all_messages", response_model=list[MessageResponse])
async def get_all_messages(partnerID: int,user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).filter_by(id=partnerID))
        partner = result.scalar_one_or_none()

        if partner is None:
            logger.error("Partner does not exist")
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail={"message":"Partner does not exist"}
            )
        return await get_messages(db, user.id, partner.id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message":str(e)}
        )

@router.websocket("/ws")
async def core_chatting(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db),
    chat_hub: ChatHub = Depends(get_chatHub)
):
    await websocket.accept()

    try:
        payload = decode_jwt_token(token)
        username = payload.get("sub")
        if not username:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user = await get_user_by_username(db=db,username=username)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = user.id
        await chat_hub.connect(websocket, user_id)

    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        while True:
                raw_data = await websocket.receive_text()

                try:
                    data_json = json.loads(raw_data)

                    message_payload = MessageCreate(**data_json)

                    message = await create_message(db, message_payload, user_id)

                    response_data = {
                        "senderID": message.sender_id,
                        "receiverID": message.receiver_id,
                        "content": message.content,
                        "messageType": message.message_type,
                        "attachmentID": message.attachment_id,
                        "timestamp": message.timestamp.isoformat(),
                    }

                    await chat_hub.send_to(message.receiver_id, response_data)

                    await chat_hub.send_to(user_id, response_data)

                except json.JSONDecodeError:
                    await websocket.send_text("Invalid JSON format")
                except ValidationError as ve:
                    await websocket.send_text(f"Validation error: {ve.errors()}")
                except Exception as e:
                    await websocket.send_text(f"Server error: {str(e)}")

    except WebSocketDisconnect:
        logger.error("WebSocket disconnected")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message":"Websocket disconnected"}
        )
        await chat_hub.disconnect(websocket, user_id)
