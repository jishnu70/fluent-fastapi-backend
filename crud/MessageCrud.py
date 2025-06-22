from sqlalchemy.future import select
from fastapi import HTTPException, status
from sqlalchemy import or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from models.Message import Message
from models.User import User
from schemas.MessageSchema import MessageCreate
import logging
from typing import Optional
from datetime import datetime

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
            # attachment_id=payload.attachmentID if payload.attachmentID else None
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message
    except Exception as e:
        await db.rollback()
        logger.error(e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message":str(e)})

async def get_messages(
    db:AsyncSession,
    userID: int,
    partnerID: int,
    before: Optional[datetime] = None,
    limit: int = 20,
):
    try:
        result = await db.execute(select(User).filter_by(id=partnerID))
        partner = result.scalar_one_or_none()
        if not partner:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "receiver does not exist"})

        query = select(Message).where(
            or_(
                and_(Message.sender_id==userID, Message.receiver_id==partner.id),
                and_(Message.sender_id==partner.id, Message.receiver_id==userID)
            )
        )

        if before:
            query = query.where(Message.timestamp < before)

        query = query.order_by(Message.timestamp.desc()).limit(limit).options(joinedload(Message.attachment))

        messagesResult = await db.execute(query)
        messages = messagesResult.scalars().all()
        return messages
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": str(e)})

async def get_latest_messages_per_partner(db:AsyncSession, userID: int):
    try:
        result = await db.execute(
                select(Message)
                .where(or_(Message.sender_id == userID, Message.receiver_id == userID))
                .order_by(Message.timestamp.desc())
                .options(joinedload(Message.attachment))
            )
        messages = result.scalars().all()

        latest_messages = {}

        for msg in messages:
            partner_id = msg.receiver_id if msg.sender_id == userID else msg.sender_id
            if partner_id not in latest_messages:
                partner_result = await db.execute(select(User).where(User.id == partner_id))
                partner = partner_result.scalars().first()
                if partner:
                    latest_messages[partner_id] = (partner, msg)

        return list(latest_messages.values())
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": str(e)})
