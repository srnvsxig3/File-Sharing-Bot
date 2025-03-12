import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNEL, ADMINS
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait


async def is_subscribed(filter, client, update):
    if not FORCE_SUB_CHANNEL:
        return True  # If no force sub is set, allow access

    user_id = update.from_user.id
    if user_id in ADMINS:
        return True  # Admins don't need to subscribe

    try:
        # Get user membership status using Channel ID
        member = await client.get_chat_member(chat_id=int(FORCE_SUB_CHANNEL), user_id=user_id)
        print(f"🔹 User ID: {user_id}, Status: {member.status}")  # Debug log

    except UserNotParticipant:
        print(f"🚫 User {user_id} is NOT a participant in {FORCE_SUB_CHANNEL}!")  # Debug log
        return False  # User is not in the channel

    except Exception as e:
        print(f"⚠️ Error checking subscription: {e}")  # Debug log
        return False  # Any unexpected error

    # Allow only if user is an Owner, Admin, or Member
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return (base64_bytes.decode("ascii")).strip("=")


async def decode(base64_string):
    base64_string = base64_string.strip("=")  # Handle padding errors
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    return base64.urlsafe_b64decode(base64_bytes).decode("ascii")


async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temp_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=temp_ids)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=temp_ids)
        except:
            pass
        total_messages += len(temp_ids)
        messages.extend(msgs)
    return messages


async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id, msg_id = matches.groups()
        if channel_id.isdigit():
            return msg_id if f"-100{channel_id}" == str(client.db_channel.id) else 0
        return msg_id if channel_id == client.db_channel.username else 0
    return 0


def get_readable_time(seconds: int) -> str:
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    count = 0
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60 if count < 3 else 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(f"{int(result)}{time_suffix_list[count-1]}")
        seconds = int(remainder)
    return ":".join(reversed(time_list))


subscribed = filters.create(is_subscribed)

# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
