"""
Configuration settings for the BGMI Tournament Bot
"""

import os

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7438267281:AAHzn5fuLbWtJWtqtzXV36bN-XM0pD15a14")
    ADMIN_ID = int(os.getenv("ADMIN_ID", "7891142412"))
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@Officialbgmi24")
    
    # Payment Configuration
    UPI_ID = os.getenv("UPI_ID", "8435010927@ybl")
    
    # Channel Configuration
    CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/KyaTereSquadMeinDumHai")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "-1002880573048")  # Added negative prefix for supergroup
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://rahul7241146384:rahul7241146384@cluster0.qeaogc4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "bgmi_tournament_bot")
    
    # AI Configuration
    AI_API_KEY = os.getenv("AI_API_KEY", "d96a2478-7fde-4d76-a28d-b8172e561077")
    
    # Tournament Configuration
    MAX_SQUAD_SIZE = 4
    MIN_ENTRY_FEE = 10
    MAX_ENTRY_FEE = 500
    
    # Notification Times (24-hour format)
    NOTIFICATION_TIMES = {
        "morning": "08:00",
        "afternoon": "14:00", 
        "evening": "18:00",
        "night": "22:00"
    }
