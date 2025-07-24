#!/usr/bin/env python3
"""
BGMI Tournament Bot - Main Entry Point
Bot name: Kya Tere Squad Mein Dum Hai
"""

import asyncio
import logging
import os
from telegram.ext import Application

from bot.handlers import setup_handlers
from bot.database import init_database
from bot.notifications import start_notification_scheduler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot"""
    try:
        # Create application
        application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Setup handlers
        setup_handlers(application)
        logger.info("Handlers setup completed")
        
        # Add post-init callback to setup database and notifications
        async def post_init(app):
            await init_database()
            logger.info("Database initialized successfully")
            await start_notification_scheduler(app.bot)
            logger.info("Notification scheduler started")
        
        # Register the post-init callback
        application.post_init = post_init
        
        # Start the bot
        logger.info("Starting BGMI Tournament Bot...")
        application.run_polling(allowed_updates=["message", "callback_query"], drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    main()
