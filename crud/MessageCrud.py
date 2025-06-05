from sqlalchemy.future import select
from fastapi import HTTPException, status
from sqlalchemy import or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from models.Message import Message
from models.User import User
from schemas.MessageSchema import MessageCreate
import logging

logger = logging.getLogger(__name__)

async def create_message(db: AsyncSession, payload:MessageCreate, senderID: int):
    try:
        result = await db.execute(select(User).filter_by(id=payload.receiverID))
        receiver = result.scalar_one_or_none()
        if not receiver:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "receiver does not exist"})
        message = Message(
            sender_id=senderID,
            receiver_id=receiver.id,
            content=payload.content,
            message_type=payload.messageType,
            attachment_id=payload.attachmentID if payload.attachmentID else None
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message":str(e)})
    
async def get_messages(db:AsyncSession, userID: int, partnerID: int):
    try:
        result = await db.execute(select(User).filter_by(id=partnerID))
        partner = result.scalar_one_or_none()
        if not partner:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "receiver does not exist"})
        
        messagesResult = await db.execute(
            select(Message)
            .where(
                and_(
                    or_(Message.sender_id==userID, Message.receiver_id==userID),
                    or_(Message.sender_id==partner.id, Message.receiver_id==partner.id)
                )
            )
            .options(joinedload(Message.attachment))
        )
        messages = messagesResult.scalars().all()
        return messages
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": str(e)})