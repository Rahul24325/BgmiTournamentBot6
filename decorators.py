"""
Decorators for access control and permissions
"""

import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from .config import Config

logger = logging.getLogger(__name__)

def admin_only(func):
    """Decorator to restrict command to admin only"""
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_ID:
            await update.message.reply_text(
                "❌ **Access Denied**\n\n"
                "This command is only available to administrators.\n"
                f"Contact {Config.ADMIN_USERNAME} for assistance.",
                parse_mode='Markdown'
            )
            return
        
        return await func(self, update, context)
    return wrapper

def channel_required(func):
    """Decorator to check if user has joined the required channel"""
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        # Skip check for admin
        if user_id == Config.ADMIN_ID:
            return await func(self, update, context)
        
        try:
            # Check if user is member of the channel
            member = await context.bot.get_chat_member(Config.CHANNEL_ID, user_id)
            
            if member.status in ['member', 'administrator', 'creator']:
                return await func(self, update, context)
            else:
                await update.message.reply_text(
                    "🚫 **Channel Membership Required**\n\n"
                    "You must join our official channel to use this bot.\n\n"
                    f"👉 [Join Channel]({Config.CHANNEL_URL})\n\n"
                    "After joining, send /start again.",
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                return
                
        except Exception as e:
            logger.error(f"Error checking channel membership: {e}")
            await update.message.reply_text(
                "⚠️ **Unable to verify channel membership**\n\n"
                f"Please ensure you've joined: {Config.CHANNEL_URL}\n\n"
                "Then try again.",
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            return
    
    return wrapper

def error_handler(func):
    """Decorator for error handling"""
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            return await func(self, update, context)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            
            error_message = (
                "❌ **An error occurred**\n\n"
                "Please try again later or contact support.\n"
                f"Admin: {Config.ADMIN_USERNAME}"
            )
            
            if update.message:
                await update.message.reply_text(error_message, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.message.reply_text(error_message, parse_mode='Markdown')
    
    return wrapper
