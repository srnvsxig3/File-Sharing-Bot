from pyrogram import Client, filters
from pyrogram.types import Message
from helper_func import subscribed
from config import FORCE_SUB_CHANNEL

@Client.on_message(filters.private & subscribed)
async def handle_message(client: Client, message: Message):
    await message.reply("✅ You are subscribed! You can now use the bot.")

@Client.on_message(filters.private & ~subscribed)
async def force_sub(client: Client, message: Message):
    await message.reply(f"❌ You must join the required channel before using this bot!\n\n"
                        f"🔹 Channel ID: `{FORCE_SUB_CHANNEL}`",
                        disable_web_page_preview=True)
