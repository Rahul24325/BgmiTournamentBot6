"""
Main handlers for the BGMI Tournament Bot
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ConversationHandler
)

from .config import Config
from .database import db
from .decorators import admin_only, channel_required, error_handler
from .keyboards import Keyboards
from .messages import Messages
from .ai_service import AIService

logger = logging.getLogger(__name__)

# Conversation states
(
    TOURNAMENT_NAME, TOURNAMENT_DATE, TOURNAMENT_TIME, 
    TOURNAMENT_ENTRY_FEE, TOURNAMENT_PRIZE_POOL, TOURNAMENT_MAP,
    TOURNAMENT_CUSTOM_MESSAGE, ROOM_ID_INPUT, ROOM_PASSWORD_INPUT,
    WINNER_INPUT, TDM_ROUNDS, TDM_MATCH_DURATION, TDM_TEAM_SIZE
) = range(13)

class BotHandlers:
    def __init__(self):
        self.ai_service = AIService()
        self.active_tournaments = {}
        self.user_states = {}
    
    @error_handler
    @channel_required
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Save user to database
        user_data = {
            "user_id": user_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "last_activity": datetime.utcnow()
        }
        await db.add_user(user_data)
        
        # Check if user is admin
        is_admin = user_id == Config.ADMIN_ID
        
        # Send welcome message
        welcome_msg = Messages.get_welcome_message(user.first_name, is_admin)
        keyboard = Keyboards.admin_menu() if is_admin else Keyboards.main_menu()
        
        await update.message.reply_text(
            welcome_msg,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    @error_handler
    @admin_only
    async def create_tournament_solo_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /createtournamentsolo command"""
        context.user_data['tournament_type'] = 'Solo'
        
        await update.message.reply_text(
            "🏆 **Creating Solo Tournament** 🏆\n\n"
            "Let's set up an epic solo battle! 🎮\n\n"
            "📝 **Step 1/7:** Enter tournament name\n"
            "Example: 'Friday Night Solo Championship'",
            parse_mode='Markdown'
        )
        
        return TOURNAMENT_NAME
    
    @error_handler
    @admin_only
    async def create_tournament_squad_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /createtournamentsqaud command"""
        context.user_data['tournament_type'] = 'Squad'
        
        await update.message.reply_text(
            "👥 **Creating Squad Tournament** 👥\n\n"
            "Time for some team action! 🔥\n\n"
            "📝 **Step 1/7:** Enter tournament name\n"
            "Example: 'Saturday Squad Showdown'",
            parse_mode='Markdown'
        )
        
        return TOURNAMENT_NAME
    
    @error_handler
    @admin_only
    async def create_tournament_tdm_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /createtournamenttdm command"""
        context.user_data['tournament_type'] = 'TDM'
        
        await update.message.reply_text(
            "💥 **Creating TDM Tournament** 💥\n\n"
            "Team Deathmatch mode! Pure combat! 🔥\n\n"
            "📝 **Step 1/10:** Enter tournament name\n"
            "Example: 'TDM Friday Night Clash'",
            parse_mode='Markdown'
        )
        
        return TOURNAMENT_NAME
    
    async def tournament_name_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament name input"""
        tournament_name = update.message.text.strip()
        
        if len(tournament_name) < 5:
            await update.message.reply_text(
                "❌ **Tournament name too short!**\n\n"
                "Please enter a name with at least 5 characters.\n"
                "Make it exciting and memorable! 🎮"
            )
            return TOURNAMENT_NAME
        
        context.user_data['tournament_name'] = tournament_name
        
        await update.message.reply_text(
            f"✅ **Tournament Name Set:** {tournament_name}\n\n"
            "📝 **Step 2/7:** Enter tournament date\n"
            "Format: DD/MM/YYYY\n"
            "Example: 25/07/2025"
        )
        
        return TOURNAMENT_DATE
    
    async def tournament_date_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament date input"""
        date_text = update.message.text.strip()
        
        try:
            # Validate date format
            tournament_date = datetime.strptime(date_text, "%d/%m/%Y")
            
            # Check if date is in future
            if tournament_date.date() < datetime.now().date():
                await update.message.reply_text(
                    "❌ **Date cannot be in the past!**\n\n"
                    "Please enter a future date.\n"
                    "Format: DD/MM/YYYY"
                )
                return TOURNAMENT_DATE
            
            context.user_data['tournament_date'] = date_text
            
            await update.message.reply_text(
                f"✅ **Date Set:** {date_text}\n\n"
                "📝 **Step 3/7:** Enter tournament time\n"
                "Format: HH:MM (24-hour)\n"
                "Example: 20:00 or 14:30"
            )
            
            return TOURNAMENT_TIME
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid date format!**\n\n"
                "Please use DD/MM/YYYY format.\n"
                "Example: 25/07/2025"
            )
            return TOURNAMENT_DATE
    
    async def tournament_time_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament time input"""
        time_text = update.message.text.strip()
        
        try:
            # Validate time format
            datetime.strptime(time_text, "%H:%M")
            context.user_data['tournament_time'] = time_text
            
            await update.message.reply_text(
                f"✅ **Time Set:** {time_text}\n\n"
                "📝 **Step 4/7:** Enter entry fee (₹)\n"
                f"Minimum: ₹{Config.MIN_ENTRY_FEE} | Maximum: ₹{Config.MAX_ENTRY_FEE}\n"
                "Example: 50"
            )
            
            return TOURNAMENT_ENTRY_FEE
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid time format!**\n\n"
                "Please use HH:MM format (24-hour).\n"
                "Example: 20:00 or 14:30"
            )
            return TOURNAMENT_TIME
    
    async def tournament_entry_fee_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament entry fee input"""
        try:
            entry_fee = int(update.message.text.strip())
            
            if entry_fee < Config.MIN_ENTRY_FEE or entry_fee > Config.MAX_ENTRY_FEE:
                await update.message.reply_text(
                    f"❌ **Entry fee out of range!**\n\n"
                    f"Please enter amount between ₹{Config.MIN_ENTRY_FEE} and ₹{Config.MAX_ENTRY_FEE}"
                )
                return TOURNAMENT_ENTRY_FEE
            
            context.user_data['tournament_entry_fee'] = entry_fee
            
            # Get AI suggestion for prize pool
            ai_suggestion = await self.ai_service.suggest_prize_pool(entry_fee)
            
            await update.message.reply_text(
                f"✅ **Entry Fee Set:** ₹{entry_fee}\n\n"
                f"💡 **AI Suggestion:** ₹{ai_suggestion}\n\n"
                "📝 **Step 5/7:** Enter total prize pool (₹)\n"
                "Example: 500"
            )
            
            return TOURNAMENT_PRIZE_POOL
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid amount!**\n\n"
                "Please enter a valid number.\n"
                "Example: 50"
            )
            return TOURNAMENT_ENTRY_FEE
    
    async def tournament_prize_pool_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament prize pool input"""
        try:
            prize_pool = int(update.message.text.strip())
            
            if prize_pool <= 0:
                await update.message.reply_text(
                    "❌ **Prize pool must be greater than 0!**\n\n"
                    "Please enter a valid amount."
                )
                return TOURNAMENT_PRIZE_POOL
            
            context.user_data['tournament_prize_pool'] = prize_pool
            
            await update.message.reply_text(
                f"✅ **Prize Pool Set:** ₹{prize_pool}\n\n"
                "📝 **Step 6/7:** Enter map name\n"
                "Examples: Erangel, Sanhok, Miramar, Livik\n"
                "Or type 'Random' for random map selection"
            )
            
            return TOURNAMENT_MAP
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid amount!**\n\n"
                "Please enter a valid number.\n"
                "Example: 500"
            )
            return TOURNAMENT_PRIZE_POOL
    
    async def tournament_map_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament map input"""
        map_name = update.message.text.strip()
        context.user_data['tournament_map'] = map_name
        
        # Check if it's TDM tournament - if so, need additional configuration
        if context.user_data.get('tournament_type') == 'TDM':
            await update.message.reply_text(
                f"✅ **Map Set:** {map_name}\n\n"
                "📝 **Step 7/10:** Enter number of rounds\n"
                "TDM matches consist of multiple rounds.\n"
                "Recommended: 3-5 rounds\n"
                "Example: 5"
            )
            return TDM_ROUNDS
        else:
            await update.message.reply_text(
                f"✅ **Map Set:** {map_name}\n\n"
                "📝 **Step 7/7:** Enter custom message (optional)\n"
                "This will be added to tournament announcement.\n"
                "Type 'skip' to skip this step.\n\n"
                "Example: 'Special weekend tournament with bonus prizes!'"
            )
            return TOURNAMENT_CUSTOM_MESSAGE
    
    async def tdm_rounds_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle TDM rounds input"""
        try:
            rounds = int(update.message.text.strip())
            
            if rounds < 1 or rounds > 10:
                await update.message.reply_text(
                    "❌ **Invalid number of rounds!**\n\n"
                    "Please enter a number between 1 and 10.\n"
                    "Recommended: 3-5 rounds"
                )
                return TDM_ROUNDS
            
            context.user_data['tdm_rounds'] = rounds
            
            await update.message.reply_text(
                f"✅ **Rounds Set:** {rounds}\n\n"
                "📝 **Step 8/10:** Enter match duration (minutes)\n"
                "How long should each round last?\n"
                "Recommended: 5-10 minutes\n"
                "Example: 8"
            )
            
            return TDM_MATCH_DURATION
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid number!**\n\n"
                "Please enter a valid number.\n"
                "Example: 5"
            )
            return TDM_ROUNDS
    
    async def tdm_match_duration_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle TDM match duration input"""
        try:
            duration = int(update.message.text.strip())
            
            if duration < 3 or duration > 30:
                await update.message.reply_text(
                    "❌ **Invalid duration!**\n\n"
                    "Please enter a duration between 3 and 30 minutes.\n"
                    "Recommended: 5-10 minutes"
                )
                return TDM_MATCH_DURATION
            
            context.user_data['tdm_match_duration'] = duration
            
            await update.message.reply_text(
                f"✅ **Duration Set:** {duration} minutes\n\n"
                "📝 **Step 9/10:** Enter team size\n"
                "How many players per team?\n"
                "Options: 2v2, 3v3, 4v4, 5v5\n"
                "Example: 4"
            )
            
            return TDM_TEAM_SIZE
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid number!**\n\n"
                "Please enter a valid number.\n"
                "Example: 8"
            )
            return TDM_MATCH_DURATION
    
    async def tdm_team_size_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle TDM team size input"""
        try:
            team_size = int(update.message.text.strip())
            
            if team_size < 2 or team_size > 5:
                await update.message.reply_text(
                    "❌ **Invalid team size!**\n\n"
                    "Please enter a number between 2 and 5.\n"
                    "Standard options: 2v2, 3v3, 4v4, 5v5"
                )
                return TDM_TEAM_SIZE
            
            context.user_data['tdm_team_size'] = team_size
            
            await update.message.reply_text(
                f"✅ **Team Size Set:** {team_size}v{team_size}\n\n"
                "📝 **Step 10/10:** Enter custom message (optional)\n"
                "This will be added to tournament announcement.\n"
                "Type 'skip' to skip this step.\n\n"
                "Example: 'Epic TDM showdown with custom rules!'"
            )
            
            return TOURNAMENT_CUSTOM_MESSAGE
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid number!**\n\n"
                "Please enter a valid number.\n"
                "Example: 4"
            )
            return TDM_TEAM_SIZE
    
    async def tournament_custom_message_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tournament custom message input"""
        custom_message = update.message.text.strip()
        
        if custom_message.lower() != 'skip':
            context.user_data['tournament_custom_message'] = custom_message
        
        # Create tournament in database
        tournament_data = {
            'name': context.user_data['tournament_name'],
            'type': context.user_data['tournament_type'],
            'date': context.user_data['tournament_date'],
            'time': context.user_data['tournament_time'],
            'entry_fee': context.user_data['tournament_entry_fee'],
            'prize_pool': context.user_data['tournament_prize_pool'],
            'map': context.user_data['tournament_map'],
            'custom_message': context.user_data.get('tournament_custom_message', ''),
            'admin_id': update.effective_user.id
        }
        
        # Add TDM-specific data if it's a TDM tournament
        if context.user_data.get('tournament_type') == 'TDM':
            tournament_data.update({
                'tdm_rounds': context.user_data.get('tdm_rounds', 5),
                'tdm_match_duration': context.user_data.get('tdm_match_duration', 8),
                'tdm_team_size': context.user_data.get('tdm_team_size', 4)
            })
        
        tournament_id = await db.create_tournament(tournament_data)
        
        if tournament_id:
            # Store tournament for quick access
            self.active_tournaments[tournament_id] = tournament_data
            
            # Send tournament announcement to channel
            announcement = Messages.tournament_announcement(tournament_data)
            keyboard = Keyboards.tournament_join(tournament_id)
            
            try:
                await context.bot.send_message(
                    chat_id=Config.CHANNEL_ID,
                    text=announcement,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
                await update.message.reply_text(
                    "🎉 **Tournament Created Successfully!** 🎉\n\n"
                    f"🏆 **{tournament_data['name']}**\n"
                    f"📅 {tournament_data['date']} at {tournament_data['time']}\n"
                    f"💰 Entry: ₹{tournament_data['entry_fee']} | Prize: ₹{tournament_data['prize_pool']}\n\n"
                    "✅ Tournament announced in channel\n"
                    "📊 Players can now register!\n\n"
                    f"🆔 **Tournament ID:** `{tournament_id}`",
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                logger.error(f"Error sending tournament announcement: {e}")
                await update.message.reply_text(
                    "⚠️ **Tournament created but announcement failed**\n\n"
                    "Tournament is saved in database but couldn't post to channel.\n"
                    "Please check channel permissions."
                )
        else:
            await update.message.reply_text(
                "❌ **Failed to create tournament**\n\n"
                "Please try again or contact technical support."
            )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END
    
    async def cancel_tournament_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel tournament creation"""
        context.user_data.clear()
        await update.message.reply_text(
            "❌ **Tournament creation cancelled**\n\n"
            "No worries! You can start again anytime.\n"
            "Use /createtournamentsolo or /createtournamentsqaud"
        )
        return ConversationHandler.END
    
    @error_handler
    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        # Tournament join handling
        if data.startswith("join_"):
            tournament_id = data.replace("join_", "")
            await self.handle_tournament_join(query, tournament_id)
        
        # Payment confirmation
        elif data == "payment_done":
            await self.handle_payment_done(query)
        
        # Rules and info
        elif data == "rules":
            await self.show_rules_menu(query)
        elif data == "tournament_rules":
            await self.show_tournament_rules(query)
        elif data == "payment_info":
            await self.show_payment_info(query)
        elif data == "disclaimer":
            await self.show_disclaimer(query)
        
        # Admin callbacks
        elif data == "admin_menu" and user_id == Config.ADMIN_ID:
            await self.show_admin_menu(query)
        elif data == "earnings_menu" and user_id == Config.ADMIN_ID:
            await self.show_earnings_menu(query)
        elif data.startswith("earnings_") and user_id == Config.ADMIN_ID:
            period = data.replace("earnings_", "")
            await self.show_earnings_report(query, period)
        
        # Payment confirmation callbacks (admin only)
        elif data.startswith("admin_confirm_") and user_id == Config.ADMIN_ID:
            username = data.replace("admin_confirm_", "")
            await self.handle_admin_confirm_payment(query, username)
        elif data.startswith("admin_decline_") and user_id == Config.ADMIN_ID:
            username = data.replace("admin_decline_", "")
            await self.handle_admin_decline_payment(query, username)
        
        # Main menu
        elif data == "main_menu":
            await self.show_main_menu(query)
    
    async def handle_tournament_join(self, query, tournament_id: str):
        """Handle tournament join request"""
        user = query.from_user
        user_id = user.id
        
        # Get tournament data
        tournament = await db.get_tournament(tournament_id)
        if not tournament:
            await query.edit_message_text(
                "❌ **Tournament not found**\n\n"
                "This tournament may have been deleted or completed."
            )
            return
        
        # Check if user already registered
        if user_id in tournament.get('participants', []):
            await query.edit_message_text(
                "ℹ️ **Already Registered**\n\n"
                "You're already registered for this tournament!\n"
                "Wait for payment confirmation from admin."
            )
            return
        
        # Add participant to tournament
        await db.add_participant(tournament_id, user_id)
        
        # Show payment instructions
        payment_msg = Messages.payment_instructions(tournament, user.first_name)
        keyboard = Keyboards.payment_confirmation()
        
        await query.edit_message_text(
            payment_msg,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Store tournament ID for payment confirmation
        context = query._bot._callback_context if hasattr(query._bot, '_callback_context') else None
        if context:
            context.user_data['current_tournament_id'] = tournament_id
    
    async def handle_payment_done(self, query):
        """Handle payment done confirmation"""
        user = query.from_user
        user_id = user.id
        
        # Add payment record
        payment_data = {
            "user_id": user_id,
            "username": user.username,
            "first_name": user.first_name,
            "tournament_id": "pending",  # Will be updated when admin confirms
            "amount": 0,  # Will be updated from tournament data
            "status": "pending"
        }
        
        await db.add_payment(payment_data)
        
        # Send confirmation message
        confirmation_msg = Messages.payment_confirmation_pending()
        await query.edit_message_text(confirmation_msg, parse_mode='Markdown')
        
        # Notify admin
        try:
            admin_notification = (
                f"💰 **New Payment Confirmation** 💰\n\n"
                f"👤 **User:** {user.first_name} (@{user.username})\n"
                f"🆔 **User ID:** {user_id}\n"
                f"⏰ **Time:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"Use buttons below or commands:\n"
                f"`/confirm @{user.username}`\n"
                f"`/decline @{user.username}`"
            )
            
            # Create admin action keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ Confirm", callback_data=f"admin_confirm_{user.username}"),
                    InlineKeyboardButton("❌ Decline", callback_data=f"admin_decline_{user.username}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query._bot.send_message(
                chat_id=Config.ADMIN_ID,
                text=admin_notification,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error notifying admin: {e}")
    
    @error_handler
    @admin_only
    async def confirm_payment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /confirm @username command"""
        if not context.args:
            await update.message.reply_text(
                "❌ **Username required**\n\n"
                "Usage: `/confirm @username`\n"
                "Example: `/confirm @john_doe`",
                parse_mode='Markdown'
            )
            return
        
        username = context.args[0].replace('@', '')
        
        # Get user by username
        user_doc = await db.db.users.find_one({"username": username})
        if not user_doc:
            await update.message.reply_text(
                f"❌ **User @{username} not found**\n\n"
                "Make sure the username is correct and user has used the bot."
            )
            return
        
        user_id = user_doc['user_id']
        
        # Get user's active tournament
        active_tournaments = await db.get_active_tournaments()
        user_tournament = None
        
        for tournament in active_tournaments:
            if user_id in tournament.get('participants', []):
                user_tournament = tournament
                break
        
        if not user_tournament:
            await update.message.reply_text(
                f"❌ **No active registration found for @{username}**\n\n"
                "User hasn't registered for any active tournament."
            )
            return
        
        # Confirm player in tournament
        tournament_id = user_tournament.get('tournament_id') or user_tournament.get('_id')
        if not tournament_id:
            # Fallback to first available tournament ID
            tournament_id = str(user_tournament.get('_id', ''))
        
        await db.confirm_player(tournament_id, user_id)
        await db.confirm_payment(user_id, tournament_id)
        
        # Send confirmation to user
        try:
            confirmation_msg = Messages.payment_confirmed(user_tournament)
            await context.bot.send_message(
                chat_id=user_id,
                text=confirmation_msg,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending confirmation to user: {e}")
        
        # Confirm to admin
        await update.message.reply_text(
            f"✅ **Payment Confirmed** ✅\n\n"
            f"👤 **Player:** @{username}\n"
            f"🏆 **Tournament:** {user_tournament['name']}\n"
            f"💰 **Entry Fee:** ₹{user_tournament['entry_fee']}\n\n"
            "Player has been notified and confirmed for the tournament!"
        )
    
    @error_handler
    @admin_only
    async def decline_payment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /decline @username command"""
        if not context.args:
            await update.message.reply_text(
                "❌ **Username required**\n\n"
                "Usage: `/decline @username`\n"
                "Example: `/decline @john_doe`",
                parse_mode='Markdown'
            )
            return
        
        username = context.args[0].replace('@', '')
        
        # Get user by username
        user_doc = await db.db.users.find_one({"username": username})
        if not user_doc:
            await update.message.reply_text(
                f"❌ **User @{username} not found**\n\n"
                "Make sure the username is correct."
            )
            return
        
        user_id = user_doc['user_id']
        
        # Find and decline user's participation
        active_tournaments = await db.get_active_tournaments()
        user_tournament = None
        
        for tournament in active_tournaments:
            if user_id in tournament.get('participants', []):
                user_tournament = tournament
                tournament_id = tournament.get('tournament_id') or str(tournament.get('_id', ''))
                await db.remove_participant(tournament_id, user_id)
                await db.decline_payment(user_id)
                break
        
        if not user_tournament:
            await update.message.reply_text(
                f"❌ **No registration found for @{username}**"
            )
            return
        
        # Send decline message to user
        try:
            decline_msg = Messages.payment_declined()
            await context.bot.send_message(
                chat_id=user_id,
                text=decline_msg,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending decline message to user: {e}")
        
        # Confirm to admin
        await update.message.reply_text(
            f"❌ **Payment Declined** ❌\n\n"
            f"👤 **Player:** @{username}\n"
            f"🏆 **Tournament:** {user_tournament['name']}\n\n"
            "Player has been notified and removed from tournament."
        )
    
    async def handle_admin_confirm_payment(self, query, username: str):
        """Handle admin confirm payment via button"""
        try:
            # Get user by username
            user_doc = await db.db.users.find_one({"username": username})
            if not user_doc:
                await query.edit_message_text(
                    f"❌ **User @{username} not found**\n\n"
                    "Make sure the username is correct."
                )
                return
            
            user_id = user_doc['user_id']
            
            # Get user's active tournament
            active_tournaments = await db.get_active_tournaments()
            user_tournament = None
            
            for tournament in active_tournaments:
                if user_id in tournament.get('participants', []):
                    user_tournament = tournament
                    break
            
            if not user_tournament:
                await query.edit_message_text(
                    f"❌ **No active registration found for @{username}**"
                )
                return
            
            # Confirm player in tournament
            tournament_id = user_tournament.get('tournament_id') or str(user_tournament.get('_id', ''))
            await db.confirm_player(tournament_id, user_id)
            await db.confirm_payment(user_id, tournament_id)
            
            # Send confirmation to user
            try:
                confirmation_msg = Messages.payment_confirmed(user_tournament)
                await query._bot.send_message(
                    chat_id=user_id,
                    text=confirmation_msg,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending confirmation to user: {e}")
            
            # Update admin message
            await query.edit_message_text(
                f"✅ **Payment Confirmed** ✅\n\n"
                f"👤 **Player:** @{username}\n"
                f"🏆 **Tournament:** {user_tournament['name']}\n"
                f"💰 **Entry Fee:** ₹{user_tournament['entry_fee']}\n\n"
                "Player has been notified and confirmed for the tournament!"
            )
            
        except Exception as e:
            logger.error(f"Error in admin confirm: {e}")
            await query.edit_message_text(
                f"❌ **Error confirming payment for @{username}**\n\n"
                "Please try using the command: `/confirm @{username}`"
            )
    
    async def handle_admin_decline_payment(self, query, username: str):
        """Handle admin decline payment via button"""
        try:
            # Get user by username
            user_doc = await db.db.users.find_one({"username": username})
            if not user_doc:
                await query.edit_message_text(
                    f"❌ **User @{username} not found**"
                )
                return
            
            user_id = user_doc['user_id']
            
            # Get user's active tournament
            active_tournaments = await db.get_active_tournaments()
            user_tournament = None
            
            for tournament in active_tournaments:
                if user_id in tournament.get('participants', []):
                    user_tournament = tournament
                    break
            
            if not user_tournament:
                await query.edit_message_text(
                    f"❌ **No active registration found for @{username}**"
                )
                return
            
            # Remove participant and decline payment
            tournament_id = user_tournament.get('tournament_id') or str(user_tournament.get('_id', ''))
            await db.remove_participant(tournament_id, user_id)
            await db.decline_payment(user_id)
            
            # Send decline message to user
            try:
                decline_msg = Messages.payment_declined()
                await query._bot.send_message(
                    chat_id=user_id,
                    text=decline_msg,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending decline message to user: {e}")
            
            # Update admin message
            await query.edit_message_text(
                f"❌ **Payment Declined** ❌\n\n"
                f"👤 **Player:** @{username}\n"
                f"🏆 **Tournament:** {user_tournament['name']}\n\n"
                "Player has been notified and removed from tournament."
            )
            
        except Exception as e:
            logger.error(f"Error in admin decline: {e}")
            await query.edit_message_text(
                f"❌ **Error declining payment for @{username}**\n\n"
                "Please try using the command: `/decline @{username}`"
            )
    
    @error_handler
    @admin_only
    async def send_room_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sendroom command"""
        active_tournaments = await db.get_active_tournaments()
        
        if not active_tournaments:
            await update.message.reply_text(
                "❌ **No active tournaments found**\n\n"
                "Create a tournament first!"
            )
            return
        
        # For simplicity, take the first active tournament
        tournament = active_tournaments[0]
        confirmed_players = tournament.get('confirmed_players', [])
        
        if not confirmed_players:
            await update.message.reply_text(
                "❌ **No confirmed players found**\n\n"
                "Confirm some players first!"
            )
            return
        
        await update.message.reply_text(
            "🎮 **Room Details Required** 🎮\n\n"
            f"📊 **Tournament:** {tournament['name']}\n"
            f"👥 **Confirmed Players:** {len(confirmed_players)}\n\n"
            "📝 Enter Room ID:"
        )
        
        context.user_data['room_tournament'] = tournament
        return ROOM_ID_INPUT
    
    async def room_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle room ID input"""
        room_id = update.message.text.strip()
        context.user_data['room_id'] = room_id
        
        await update.message.reply_text(
            f"✅ **Room ID Set:** {room_id}\n\n"
            "🔐 Enter Room Password:"
        )
        
        return ROOM_PASSWORD_INPUT
    
    async def room_password_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle room password input and send room details"""
        room_password = update.message.text.strip()
        tournament = context.user_data['room_tournament']
        room_id = context.user_data['room_id']
        
        confirmed_players = tournament.get('confirmed_players', [])
        success_count = 0
        
        # Send room details to all confirmed players
        for user_id in confirmed_players:
            try:
                room_msg = Messages.room_details(tournament, room_id, room_password)
                await context.bot.send_message(
                    chat_id=user_id,
                    text=room_msg,
                    parse_mode='Markdown'
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Error sending room details to {user_id}: {e}")
        
        await update.message.reply_text(
            f"✅ **Room Details Sent!** ✅\n\n"
            f"📤 **Sent to:** {success_count}/{len(confirmed_players)} players\n"
            f"🆔 **Room ID:** {room_id}\n"
            f"🔐 **Password:** {room_password}\n\n"
            "Tournament is now live! 🎮"
        )
        
        context.user_data.clear()
        return ConversationHandler.END
    
    @error_handler
    @admin_only
    async def list_players_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listplayers command"""
        active_tournaments = await db.get_active_tournaments()
        
        if not active_tournaments:
            await update.message.reply_text(
                "❌ **No active tournaments found**"
            )
            return
        
        response = "👥 **ACTIVE TOURNAMENT PLAYERS** 👥\n\n"
        
        for tournament in active_tournaments:
            confirmed_players = tournament.get('confirmed_players', [])
            participants = tournament.get('participants', [])
            
            response += (
                f"🏆 **{tournament['name']}**\n"
                f"📅 {tournament['date']} at {tournament['time']}\n"
                f"💰 Entry: ₹{tournament['entry_fee']}\n"
                f"✅ **Confirmed:** {len(confirmed_players)}\n"
                f"⏳ **Pending:** {len(participants) - len(confirmed_players)}\n\n"
            )
            
            if confirmed_players:
                response += "**Confirmed Players:**\n"
                for user_id in confirmed_players[:5]:  # Show first 5
                    try:
                        user = await db.get_user(user_id)
                        if user:
                            response += f"• {user.get('first_name', 'Unknown')} (@{user.get('username', 'N/A')})\n"
                    except:
                        pass
                
                if len(confirmed_players) > 5:
                    response += f"... and {len(confirmed_players) - 5} more\n"
            
            response += "\n" + "─" * 30 + "\n\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    @error_handler
    @admin_only
    async def declare_winners_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /declarewinners command"""
        active_tournaments = await db.get_active_tournaments()
        
        if not active_tournaments:
            await update.message.reply_text(
                "❌ **No active tournaments found**"
            )
            return
        
        tournament = active_tournaments[0]  # For simplicity, use first tournament
        context.user_data['winner_tournament'] = tournament
        
        await update.message.reply_text(
            f"🏆 **Declare Winners for {tournament['name']}** 🏆\n\n"
            "📝 Enter winner details in this format:\n\n"
            "**Format:**\n"
            "1st PlayerName Kills Prize\n"
            "2nd PlayerName Kills Prize\n"
            "3rd PlayerName Kills Prize\n\n"
            "**Example:**\n"
            "1st John_BGMI 12 300\n"
            "2nd Sarah_Pro 8 150\n"
            "3rd Mike_GG 5 50"
        )
        
        return WINNER_INPUT
    
    async def winner_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle winner input and announce results"""
        winner_text = update.message.text.strip()
        tournament = context.user_data['winner_tournament']
        
        # Parse winner data
        winners = []
        lines = winner_text.split('\n')
        
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 4:
                position = parts[0]
                name = parts[1]
                kills = parts[2]
                prize = parts[3]
                
                winners.append({
                    'position': position,
                    'name': name,
                    'kills': kills,
                    'prize': prize
                })
        
        if not winners:
            await update.message.reply_text(
                "❌ **Invalid format!**\n\n"
                "Please follow the format shown above."
            )
            return WINNER_INPUT
        
        # Create winner announcement
        announcement = Messages.winner_announcement(tournament, winners)
        
        # Send announcement to channel
        try:
            await context.bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=announcement,
                parse_mode='Markdown'
            )
            
            # Close tournament
            await db.close_tournament(tournament['tournament_id'])
            
            await update.message.reply_text(
                "🎉 **Winners Announced Successfully!** 🎉\n\n"
                "✅ Results posted to channel\n"
                "✅ Tournament marked as completed\n\n"
                "Great job organizing the tournament! 🏆"
            )
            
        except Exception as e:
            logger.error(f"Error announcing winners: {e}")
            await update.message.reply_text(
                "❌ **Failed to announce winners**\n\n"
                "Please check channel permissions."
            )
        
        context.user_data.clear()
        return ConversationHandler.END
    
    @error_handler
    @admin_only
    async def clear_tournaments_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        active_tournaments = await db.get_active_tournaments()
        
        if not active_tournaments:
            await update.message.reply_text(
                "❌ **No active tournaments to clear**"
            )
            return
        
        # Delete all active tournaments
        deleted_count = 0
        for tournament in active_tournaments:
            if await db.delete_tournament(tournament['tournament_id']):
                deleted_count += 1
        
        await update.message.reply_text(
            f"🗑️ **Tournaments Cleared** 🗑️\n\n"
            f"✅ Deleted {deleted_count} tournament(s)\n"
            "Database cleaned successfully!"
        )
    
    @error_handler
    @admin_only
    async def earnings_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, period: str):
        """Handle earnings commands"""
        earnings_data = await db.get_earnings(period)
        report_msg = Messages.earnings_report(earnings_data)
        
        await update.message.reply_text(report_msg, parse_mode='Markdown')
    
    # Show menu methods
    async def show_main_menu(self, query):
        """Show main menu"""
        user_id = query.from_user.id
        is_admin = user_id == Config.ADMIN_ID
        
        welcome_msg = Messages.get_welcome_message(query.from_user.first_name, is_admin)
        keyboard = Keyboards.admin_menu() if is_admin else Keyboards.main_menu()
        
        await query.edit_message_text(
            welcome_msg,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def show_admin_menu(self, query):
        """Show admin menu"""
        await query.edit_message_text(
            "🛡️ **ADMIN CONTROL PANEL** 🛡️\n\n"
            "What would you like to do?",
            reply_markup=Keyboards.admin_menu(),
            parse_mode='Markdown'
        )
    
    async def show_earnings_menu(self, query):
        """Show earnings menu"""
        await query.edit_message_text(
            "📊 **EARNINGS REPORT** 📊\n\n"
            "Select time period:",
            reply_markup=Keyboards.earnings_menu(),
            parse_mode='Markdown'
        )
    
    async def show_earnings_report(self, query, period: str):
        """Show earnings report for period"""
        earnings_data = await db.get_earnings(period)
        report_msg = Messages.earnings_report(earnings_data)
        
        await query.edit_message_text(
            report_msg,
            reply_markup=Keyboards.earnings_menu(),
            parse_mode='Markdown'
        )
    
    async def show_rules_menu(self, query):
        """Show rules and information menu"""
        await query.edit_message_text(
            "📋 **TOURNAMENT INFORMATION** 📋\n\n"
            "What would you like to know?",
            reply_markup=Keyboards.rules_navigation(),
            parse_mode='Markdown'
        )
    
    async def show_tournament_rules(self, query):
        """Show tournament rules"""
        rules_msg = Messages.tournament_rules()
        await query.edit_message_text(
            rules_msg,
            reply_markup=Keyboards.back_button(),
            parse_mode='Markdown'
        )
    
    async def show_payment_info(self, query):
        """Show payment information"""
        payment_msg = (
            "💳 **PAYMENT INFORMATION** 💳\n\n"
            f"🔹 **UPI ID:** `{Config.UPI_ID}`\n"
            "🔹 **Accepted Methods:** UPI, PhonePe, GPay, Paytm\n"
            "🔹 **Processing Time:** 5-10 minutes\n"
            "🔹 **Verification:** Manual by admin\n\n"
            "⚠️ **Important:**\n"
            "• Send exact entry fee amount\n"
            "• Keep payment screenshot ready\n"
            "• Contact admin for any issues\n\n"
            f"📞 **Support:** {Config.ADMIN_USERNAME}"
        )
        
        await query.edit_message_text(
            payment_msg,
            reply_markup=Keyboards.back_button(),
            parse_mode='Markdown'
        )
    
    async def show_disclaimer(self, query):
        """Show legal disclaimer"""
        disclaimer_msg = Messages.disclaimer()
        await query.edit_message_text(
            disclaimer_msg,
            reply_markup=Keyboards.back_button(),
            parse_mode='Markdown'
        )

def setup_handlers(application):
    """Setup all handlers for the bot"""
    handlers = BotHandlers()
    
    # Command handlers
    application.add_handler(CommandHandler("start", handlers.start_handler))
    application.add_handler(CommandHandler("listplayers", handlers.list_players_handler))
    application.add_handler(CommandHandler("clear", handlers.clear_tournaments_handler))
    application.add_handler(CommandHandler("confirm", handlers.confirm_payment_handler))
    application.add_handler(CommandHandler("decline", handlers.decline_payment_handler))
    
    # Earnings command handlers  
    async def today_earnings(update, context):
        return await handlers.earnings_handler(update, context, "today")
    
    async def thisweek_earnings(update, context):
        return await handlers.earnings_handler(update, context, "thisweek")
    
    async def thismonth_earnings(update, context):
        return await handlers.earnings_handler(update, context, "thismonth")
    
    application.add_handler(CommandHandler("today", today_earnings))
    application.add_handler(CommandHandler("thisweek", thisweek_earnings))
    application.add_handler(CommandHandler("thismonth", thismonth_earnings))
    
    # Tournament creation conversation handler
    tournament_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("createtournamentsolo", handlers.create_tournament_solo_handler),
            CommandHandler("createtournamentsqaud", handlers.create_tournament_squad_handler),
            CommandHandler("createtournamenttdm", handlers.create_tournament_tdm_handler)
        ],
        states={
            TOURNAMENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tournament_name_input)],
            TOURNAMENT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tournament_date_input)],
            TOURNAMENT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tournament_time_input)],
            TOURNAMENT_ENTRY_FEE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tournament_entry_fee_input)],
            TOURNAMENT_PRIZE_POOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tournament_prize_pool_input)],
            TOURNAMENT_MAP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tournament_map_input)],
            TOURNAMENT_CUSTOM_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tournament_custom_message_input)],
            TDM_ROUNDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tdm_rounds_input)],
            TDM_MATCH_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tdm_match_duration_input)],
            TDM_TEAM_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.tdm_team_size_input)],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_tournament_creation)]
    )
    
    # Room details conversation handler
    room_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("sendroom", handlers.send_room_handler)],
        states={
            ROOM_ID_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.room_id_input)],
            ROOM_PASSWORD_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.room_password_input)],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_tournament_creation)]
    )
    
    # Winner declaration conversation handler
    winner_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("declarewinners", handlers.declare_winners_handler)],
        states={
            WINNER_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.winner_input)],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_tournament_creation)]
    )
    
    # Add conversation handlers
    application.add_handler(tournament_conv_handler)
    application.add_handler(room_conv_handler)
    application.add_handler(winner_conv_handler)
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handlers.callback_query_handler))
