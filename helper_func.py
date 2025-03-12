import base64
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_SUB_CHANNEL_ID, ADMINS
from pyrogram.errors import UserNotParticipant, FloodWait

# Ensure FORCE_SUB_CHANNEL_ID is an integer (e.g., -100123456789)
if isinstance(FORCE_SUB_CHANNEL_ID, str):
    FORCE_SUB_CHANNEL_ID = int(FORCE_SUB_CHANNEL_ID)

# Function to check if a user is subscribed
async def is_subscribed(filter, client, update):
    if not FORCE_SUB_CHANNEL_ID:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            return True
        else:
            return False
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

# Encoding & Decoding Functions
async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

# Function to get messages from a channel
async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except Exception as e:
            print(f"Error fetching messages: {e}")
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

# Function to extract message ID from a forwarded message or URL
async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?([-_a-zA-Z0-9]+)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    return 0

# Function to convert seconds to a readable time format
def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

# Create filter for checking subscription
subscribed = filters.create(is_subscribed)

# Force Subscription Handler
@Client.on_message(filters.private & ~subscribed)
async def force_sub_message(client, message):
    buttons = [
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/c/{FORCE_SUB_CHANNEL_ID}")],
        [InlineKeyboardButton("Check Again", callback_data="checksub")]
    ]
    await message.reply_text(
        "**🚨 You must join our channel to use this bot! 🚨**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Callback handler to check subscription again
@Client.on_callback_query(filters.regex("checksub"))
async def check_subscription(client, query):
    try:
        user = await client.get_chat_member(FORCE_SUB_CHANNEL_ID, query.from_user.id)
        if user.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            await query.message.edit_text("✅ You have successfully joined the channel. Now you can use the bot!")
        else:
            await query.answer("⚠️ You haven't joined yet!", show_alert=True)
    except:
        await query.answer("⚠️ You haven't joined yet!", show_alert=True)
