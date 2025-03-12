from aiohttp import web
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import API_HASH, API_ID, LOGGER, BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT
import pyrogram.utils

pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Force Subscription (Using Channel ID)
        if FORCE_SUB_CHANNEL:
            try:
                chat = await self.get_chat(FORCE_SUB_CHANNEL)
                self.force_sub_channel = chat.id  # Ensure it's set as an ID
                self.LOGGER(__name__).info(f"✅ Force Subscription Enabled: {chat.title} ({chat.id})")
            except Exception as e:
                self.LOGGER(__name__).warning(f"⚠️ Error with Force Sub Channel: {e}")
                sys.exit()

        # Verify Database Channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Bot is active!")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(f"⚠️ Error with DB Channel: {e}")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"🤖 Bot Running Successfully! @{usr_bot_me.username}")

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("⚠️ Bot Stopped.")

if __name__ == "__main__":
    Bot().run()
