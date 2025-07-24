"""
Notification system for sending automated messages to users
"""

import asyncio
import logging
from datetime import datetime, time
from typing import List, Dict, Any
import random

from .config import Config
from .database import db
from .messages import Messages

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot):
        self.bot = bot
        self.notification_times = Config.NOTIFICATION_TIMES
        self.last_notification_time = None
        
    async def send_time_based_notifications(self):
        """Send time-based notifications (morning, afternoon, evening, night)"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            current_hour = datetime.now().hour
            
            # Determine time period
            time_period = None
            if current_time == self.notification_times["morning"]:
                time_period = "morning"
            elif current_time == self.notification_times["afternoon"]:
                time_period = "afternoon"
            elif current_time == self.notification_times["evening"]:
                time_period = "evening"
            elif current_time == self.notification_times["night"]:
                time_period = "night"
            
            if not time_period:
                return
            
            # Avoid duplicate notifications
            if self.last_notification_time == current_time:
                return
                
            self.last_notification_time = current_time
            
            # Get active users
            active_users = await db.get_all_active_users()
            if not active_users:
                logger.info("No active users for notifications")
                return
            
            # Get notification message
            notification_msg = Messages.get_notification_message(time_period)
            
            # Check for active tournaments to include in notification
            active_tournaments = await db.get_active_tournaments()
            if active_tournaments:
                tournament = active_tournaments[0]  # Feature first tournament
                tournament_info = (
                    f"\n\n🎮 **Active Tournament:**\n"
                    f"🏆 {tournament['name']}\n"
                    f"💰 Entry: ₹{tournament['entry_fee']} | Prize: ₹{tournament['prize_pool']}\n"
                    f"📅 {tournament['date']} at {tournament['time']}\n"
                    "Join now! ⚡"
                )
                notification_msg += tournament_info
            
            # Send to all active users
            success_count = 0
            for user in active_users:
                try:
                    await self.bot.send_message(
                        chat_id=user['user_id'],
                        text=notification_msg,
                        parse_mode='Markdown'
                    )
                    success_count += 1
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error sending notification to {user['user_id']}: {e}")
                    continue
            
            logger.info(f"Sent {time_period} notifications to {success_count}/{len(active_users)} users")
            
        except Exception as e:
            logger.error(f"Error in time-based notifications: {e}")
    
    async def send_tournament_notifications(self, tournament_data: Dict[str, Any]):
        """Send notifications about new tournaments"""
        try:
            active_users = await db.get_all_active_users()
            if not active_users:
                return
            
            notification_msg = Messages.new_tournament_notification(tournament_data)
            
            success_count = 0
            for user in active_users:
                try:
                    await self.bot.send_message(
                        chat_id=user['user_id'],
                        text=notification_msg,
                        parse_mode='Markdown'
                    )
                    success_count += 1
                    
                    # Delay to avoid rate limiting
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    logger.error(f"Error sending tournament notification to {user['user_id']}: {e}")
                    continue
            
            logger.info(f"Sent tournament notifications to {success_count}/{len(active_users)} users")
            
        except Exception as e:
            logger.error(f"Error in tournament notifications: {e}")
    
    async def send_reminder_notifications(self):
        """Send tournament reminder notifications"""
        try:
            active_tournaments = await db.get_active_tournaments()
            current_time = datetime.now()
            
            for tournament in active_tournaments:
                # Parse tournament datetime
                try:
                    tournament_datetime = datetime.strptime(
                        f"{tournament['date']} {tournament['time']}", 
                        "%d/%m/%Y %H:%M"
                    )
                    
                    # Check if tournament is starting in 30 minutes
                    time_diff = (tournament_datetime - current_time).total_seconds()
                    
                    if 1800 <= time_diff <= 1860:  # 30 minutes ± 1 minute
                        await self.send_tournament_reminder(tournament)
                    
                    # Check if tournament is starting in 15 minutes
                    elif 900 <= time_diff <= 960:  # 15 minutes ± 1 minute
                        await self.send_room_details_reminder(tournament)
                        
                except ValueError:
                    logger.error(f"Invalid date/time format in tournament: {tournament['tournament_id']}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in reminder notifications: {e}")
    
    async def send_tournament_reminder(self, tournament: Dict[str, Any]):
        """Send 30-minute reminder for tournament"""
        try:
            confirmed_players = tournament.get('confirmed_players', [])
            
            reminder_msg = (
                "⏰ **TOURNAMENT REMINDER** ⏰\n\n"
                f"🏆 **{tournament['name']}** starts in 30 minutes!\n\n"
                f"📅 Time: {tournament['time']}\n"
                f"🗺️ Map: {tournament.get('map', 'TBD')}\n\n"
                "🎮 **Get Ready:**\n"
                "• Keep your device charged\n"
                "• Ensure stable internet connection\n" 
                "• Room details coming in 15 minutes\n\n"
                "Good luck, champion! 🔥"
            )
            
            for user_id in confirmed_players:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=reminder_msg,
                        parse_mode='Markdown'
                    )
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error sending reminder to {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending tournament reminder: {e}")
    
    async def send_room_details_reminder(self, tournament: Dict[str, Any]):
        """Send reminder about room details availability"""
        try:
            confirmed_players = tournament.get('confirmed_players', [])
            
            reminder_msg = (
                "🚨 **ROOM DETAILS ALERT** 🚨\n\n"
                f"🏆 **{tournament['name']}** starts in 15 minutes!\n\n"
                "📢 **Waiting for room details from admin**\n"
                "Stay alert for the room ID and password!\n\n"
                "⚡ Be ready to join immediately when received!"
            )
            
            for user_id in confirmed_players:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=reminder_msg,
                        parse_mode='Markdown'
                    )
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error sending room reminder to {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending room details reminder: {e}")
    
    async def send_welcome_message_updates(self):
        """Send updated welcome messages to active users periodically"""
        try:
            # Send welcome updates every 6 hours
            current_hour = datetime.now().hour
            if current_hour not in [6, 12, 18, 0]:  # 6 AM, 12 PM, 6 PM, 12 AM
                return
            
            active_users = await db.get_all_active_users()
            if not active_users:
                return
            
            # Limit to users active in last 24 hours for welcome updates
            recent_users = [
                user for user in active_users 
                if (datetime.utcnow() - user.get('last_activity', datetime.utcnow())).days < 1
            ]
            
            if not recent_users:
                return
            
            welcome_updates = [
                "🎮 **Gaming Mode Activated!** 🎮\n\nReady for some BGMI action? New tournaments are live! 🔥",
                "⚡ **Battle Royale Alert!** ⚡\n\nChampions, your next victory awaits! Join active tournaments! 🏆",
                "🚀 **Squad Up, Warriors!** 🚀\n\nTime to dominate the battleground! Check out today's tournaments! 💪",
                "🎯 **Precision. Skill. Victory.** 🎯\n\nShow everyone what you're made of! New challenges available! 🔥"
            ]
            
            update_msg = random.choice(welcome_updates)
            
            # Add tournament info if available
            active_tournaments = await db.get_active_tournaments()
            if active_tournaments:
                tournament = active_tournaments[0]
                update_msg += (
                    f"\n\n🏆 **Featured Tournament:**\n"
                    f"📝 {tournament['name']}\n"
                    f"💰 ₹{tournament['entry_fee']} → ₹{tournament['prize_pool']}\n"
                    f"📅 {tournament['date']} at {tournament['time']}\n"
                    "Don't miss out! ⚡"
                )
            
            success_count = 0
            for user in recent_users[:50]:  # Limit to 50 users per batch
                try:
                    await self.bot.send_message(
                        chat_id=user['user_id'],
                        text=update_msg,
                        parse_mode='Markdown'
                    )
                    success_count += 1
                    await asyncio.sleep(0.2)
                except Exception as e:
                    logger.error(f"Error sending welcome update to {user['user_id']}: {e}")
                    continue
            
            logger.info(f"Sent welcome updates to {success_count} users")
            
        except Exception as e:
            logger.error(f"Error in welcome message updates: {e}")

async def notification_scheduler(bot):
    """Main notification scheduler that runs continuously"""
    notification_service = NotificationService(bot)
    
    while True:
        try:
            # Check for time-based notifications every minute
            await notification_service.send_time_based_notifications()
            
            # Check for tournament reminders every minute
            await notification_service.send_reminder_notifications()
            
            # Check for welcome message updates
            await notification_service.send_welcome_message_updates()
            
            # Wait 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in notification scheduler: {e}")
            await asyncio.sleep(60)  # Continue even if there's an error

async def start_notification_scheduler(bot):
    """Start the notification scheduler"""
    logger.info("Starting notification scheduler...")
    asyncio.create_task(notification_scheduler(bot))
