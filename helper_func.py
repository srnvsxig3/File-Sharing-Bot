import os

API_ID = 979826  # Your API ID
API_HASH = "238183386c30590d073b457166ba260d"  # Your API Hash
BOT_TOKEN = "8176887548:AAELsQbL0CxdXlCuBm69WqbMA4XrSO3gOig"  # Your Bot Token
PORT = int(os.getenv("PORT", 8080))

# Force Subscription (Using Channel ID)
FORCE_SUB_CHANNEL = -1001953560523  # Your Force Sub Channel ID

# Database Channel (Where messages are stored)
CHANNEL_ID = -1002358588449  # Your Database Channel ID

# MongoDB Database
DB_NAME = "madflixbotz"
DB_URL = "mongodb+srv://ygovcu:fY1f9Wovol3NqhUX@cluster0.1mdno.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Bot Owner (Admin User ID)
OWNER_ID = 1074804932

# List of Bot Admins
ADMINS = [OWNER_ID]  # Add more admin IDs if needed

# Logger
LOGGER = True

# Workers (How many messages to process at once)
TG_BOT_WORKERS = 10
