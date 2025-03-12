import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNEL, ADMINS
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait

async def is_subscribed(_, client, update):
    if not FORCE_SUB_CHANNEL:
        return True  # No force sub needed

    user_id = update.from_user.id
    chat_id = FORCE_SUB_CHANNEL  # Using only channel ID

    if user_id in ADMINS:
        return True  # Admins bypass force sub

    try:
        # Check if user is a member of the channel
        member = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            return True  # User is subscribed

    except UserNotParticipant:
        return False  # User not in channel

    except Exception as e:
        print(f"⚠️ Error checking subscription: {e}")
        return False  # Prevent bot crashes

    return False  # If none of the above conditions pass

subscribed = filters.create(is_subscribed)
