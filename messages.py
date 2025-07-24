"""
Message templates for the BGMI Tournament Bot
"""

import random
from datetime import datetime
from typing import Dict, Any, List

from .config import Config

class Messages:
    
    # Welcome messages (randomized)
    WELCOME_MESSAGES = [
        "🎮 **Welcome to BGMI Tournament Arena!** 🎮\n\n"
        "Kya Tere Squad Mein Dum Hai? 💪\n\n"
        "🔥 Join epic BGMI tournaments\n"
        "💰 Win amazing prizes\n"
        "🏆 Prove your skills\n\n"
        "Ready to dominate the battleground? Let's go! 🚀",
        
        "🎯 **Battle Royale Awaits You!** 🎯\n\n"
        "Squad up and show your skills! 💯\n\n"
        "⚡ Fast registration\n"
        "💸 Instant prizes\n"
        "🎪 24/7 tournaments\n\n"
        "Your chicken dinner journey starts here! 🍗",
        
        "🏹 **Enter the Arena, Champion!** 🏹\n\n"
        "Every match is a new opportunity! 🌟\n\n"
        "🎲 Multiple game modes\n"
        "🏅 Ranking system\n"
        "💎 Premium rewards\n\n"
        "Time to write your victory story! ✍️",
        
        "⚔️ **Battleground Legends Start Here!** ⚔️\n\n"
        "From zero to hero in BGMI! 🦸‍♂️\n\n"
        "🎊 Daily tournaments\n"
        "🎁 Surprise bonuses\n"
        "👑 VIP treatment\n\n"
        "Your gaming empire begins now! 🏰"
    ]
    
    @staticmethod
    def get_welcome_message(user_first_name: str, is_admin: bool = False) -> str:
        """Get randomized welcome message"""
        base_message = random.choice(Messages.WELCOME_MESSAGES)
        
        greeting = f"Hey {user_first_name}! 👋\n\n"
        
        if is_admin:
            admin_section = (
                "\n\n🛡️ **Admin Panel Access Granted**\n"
                "Tournament Commands:\n"
                "• /createtournamentsolo - Solo tournaments\n"
                "• /createtournamentsqaud - Squad tournaments\n"
                "• /createtournamenttdm - TDM tournaments\n"
                f"Earnings: /today, /thisweek, /thismonth\n"
                f"Other: /listplayers, /sendroom, /declarewinners"
            )
            return greeting + base_message + admin_section
        
        return greeting + base_message
    
    @staticmethod
    def tournament_announcement(tournament_data: Dict[str, Any]) -> str:
        """Generate tournament announcement message"""
        tournament_type = tournament_data.get('type', 'Solo').upper()
        map_name = tournament_data.get('map', 'Random')
        
        message = (
            f"🎮 **NEW {tournament_type} TOURNAMENT** 🎮\n\n"
            f"🏆 **{tournament_data['name']}**\n\n"
            f"📅 **Date:** {tournament_data['date']}\n"
            f"⏰ **Time:** {tournament_data['time']}\n"
            f"💰 **Entry Fee:** ₹{tournament_data['entry_fee']}\n"
            f"🏅 **Prize Pool:** ₹{tournament_data['prize_pool']}\n"
            f"🗺️ **Map:** {map_name}\n"
        )
        
        # Add TDM-specific details if it's a TDM tournament
        if tournament_type == 'TDM':
            rounds = tournament_data.get('tdm_rounds', 5)
            duration = tournament_data.get('tdm_match_duration', 8)
            team_size = tournament_data.get('tdm_team_size', 4)
            
            message += (
                f"🔥 **Mode:** {team_size}v{team_size} Team Deathmatch\n"
                f"🎯 **Rounds:** {rounds}\n"
                f"⏱️ **Duration:** {duration} minutes per round\n"
            )
        
        message += "\n"
        
        if tournament_data.get('custom_message'):
            message += f"📝 **Special Note:**\n{tournament_data['custom_message']}\n\n"
        
        message += (
            "🎯 **How to Join:**\n"
            "1️⃣ Click 'Join Tournament' below\n"
            "2️⃣ Complete payment process\n"
            "3️⃣ Get room details before match\n"
            "4️⃣ Win amazing prizes! 🏆\n\n"
            "⚡ **Limited Slots Available!** ⚡\n"
            "Register now before it's too late! 🔥"
        )
        
        return message
    
    @staticmethod
    def payment_instructions(tournament_data: Dict[str, Any], user_first_name: str) -> str:
        """Generate payment instructions message"""
        return (
            f"💰 **Payment Instructions for {user_first_name}** 💰\n\n"
            f"🏆 **Tournament:** {tournament_data['name']}\n"
            f"💵 **Entry Fee:** ₹{tournament_data['entry_fee']}\n\n"
            f"📱 **UPI Payment Details:**\n"
            f"UPI ID: `{Config.UPI_ID}`\n\n"
            "📋 **Payment Steps:**\n"
            "1️⃣ Open any UPI app (PhonePe, GPay, Paytm)\n"
            "2️⃣ Send exact amount to above UPI ID\n"
            "3️⃣ Take screenshot of successful payment\n"
            "4️⃣ Click 'Payment Done' below\n\n"
            "⚠️ **Important Notes:**\n"
            "• Send EXACT amount only\n"
            "• Keep payment screenshot ready\n"
            "• Admin will verify manually\n"
            "• Confirmation takes 5-10 minutes\n\n"
            "Need help? Contact admin anytime! 📞"
        )
    
    @staticmethod
    def payment_confirmation_pending() -> str:
        """Payment confirmation pending message"""
        return (
            "✅ **Payment Submission Received!** ✅\n\n"
            "🔄 **Status:** Under Review\n"
            "⏱️ **Processing Time:** 5-10 minutes\n\n"
            "📋 **What happens next:**\n"
            "1️⃣ Admin will verify your payment\n"
            "2️⃣ You'll get confirmation message\n"
            "3️⃣ Room details sent before match\n\n"
            "🚀 **Stay tuned for updates!**\n"
            f"Questions? Contact {Config.ADMIN_USERNAME}"
        )
    
    @staticmethod
    def payment_confirmed(tournament_data: Dict[str, Any]) -> str:
        """Payment confirmed message"""
        return (
            "🎉 **PAYMENT CONFIRMED!** 🎉\n\n"
            f"✅ You're registered for: **{tournament_data['name']}**\n"
            f"📅 Date: {tournament_data['date']}\n"
            f"⏰ Time: {tournament_data['time']}\n\n"
            "🎮 **Next Steps:**\n"
            "1️⃣ Room details will be sent 15 mins before match\n"
            "2️⃣ Join the room exactly on time\n"
            "3️⃣ Give your best performance\n"
            "4️⃣ Win amazing prizes! 🏆\n\n"
            "⚡ **Be ready to dominate!** ⚡\n"
            "Good luck, champion! 🚀"
        )
    
    @staticmethod
    def payment_declined() -> str:
        """Payment declined message"""
        return (
            "❌ **Payment Not Confirmed** ❌\n\n"
            "🔍 **Possible reasons:**\n"
            "• Incorrect amount sent\n"
            "• Wrong UPI ID used\n"
            "• Payment screenshot unclear\n"
            "• Technical issues\n\n"
            "🔄 **What to do:**\n"
            "1️⃣ Check payment details again\n"
            "2️⃣ Resend correct amount if needed\n"
            "3️⃣ Contact admin for assistance\n\n"
            f"📞 **Get Help:** {Config.ADMIN_USERNAME}\n"
            "We're here to help you join the tournament! 💪"
        )
    
    @staticmethod
    def room_details(tournament_data: Dict[str, Any], room_id: str, room_password: str) -> str:
        """Room details message for confirmed players"""
        return (
            f"🎮 **ROOM DETAILS - {tournament_data['name']}** 🎮\n\n"
            f"🆔 **Room ID:** `{room_id}`\n"
            f"🔐 **Password:** `{room_password}`\n\n"
            f"⏰ **Match Time:** {tournament_data['time']}\n"
            f"🗺️ **Map:** {tournament_data.get('map', 'As per room settings')}\n\n"
            "⚠️ **IMPORTANT INSTRUCTIONS:**\n"
            "1️⃣ Join room 5 minutes before match time\n"
            "2️⃣ Use your registered in-game name\n"
            "3️⃣ Don't share room details with others\n"
            "4️⃣ Follow all tournament rules\n"
            "5️⃣ Report any issues immediately\n\n"
            "🏆 **Prize Distribution:**\n"
            "Winners will be announced after match completion\n"
            "Prizes transferred within 24 hours\n\n"
            "🔥 **BEST OF LUCK, CHAMPION!** 🔥\n"
            "Show them what you're made of! 💪"
        )
    
    @staticmethod
    def winner_announcement(tournament_data: Dict[str, Any], winners: List[Dict[str, Any]]) -> str:
        """Winner announcement message"""
        message = (
            f"🏆 **TOURNAMENT RESULTS** 🏆\n\n"
            f"🎮 **{tournament_data['name']}**\n"
            f"📅 {tournament_data['date']} | ⏰ {tournament_data['time']}\n\n"
            "🎉 **CONGRATULATIONS TO OUR WINNERS!** 🎉\n\n"
        )
        
        position_emojis = ["🥇", "🥈", "🥉"]
        
        for i, winner in enumerate(winners[:3]):
            emoji = position_emojis[i] if i < 3 else f"{i+1}️⃣"
            message += (
                f"{emoji} **{winner['position']} Position**\n"
                f"👤 Player: {winner['name']}\n"
                f"🎯 Kills: {winner['kills']}\n"
                f"💰 Prize: ₹{winner['prize']}\n\n"
            )
        
        message += (
            "🎊 **Thank you all participants!** 🎊\n"
            "Every match makes you stronger! 💪\n\n"
            "📢 **Stay tuned for more tournaments!**\n"
            "Next battle is coming soon! 🚀\n\n"
            f"🎮 Join our channel: {Config.CHANNEL_URL}"
        )
        
        return message
    
    @staticmethod
    def tournament_rules() -> str:
        """Tournament rules message"""
        return (
            "📋 **BGMI TOURNAMENT RULES** 📋\n\n"
            "🎮 **General Rules:**\n"
            "1️⃣ Use your real in-game name during registration\n"
            "2️⃣ Join room 5 minutes before match time\n"
            "3️⃣ Any kind of hacking/cheating is strictly prohibited\n"
            "4️⃣ Teaming up with other squads is not allowed\n"
            "5️⃣ Admin decisions are final\n\n"
            "💰 **Payment Rules:**\n"
            "• Entry fee must be paid before room details\n"
            "• Payment confirmation required by admin\n"
            "• No refunds after room details are shared\n"
            "• Winners get prizes within 24 hours\n\n"
            "⚠️ **Fair Play Policy:**\n"
            "• Screen recording may be required\n"
            "• Suspicious activities will be investigated\n"
            "• Banned players forfeit entry fee\n"
            "• Respect all participants and admin\n\n"
            "🏆 **Prize Distribution:**\n"
            "Based on kills and final position\n"
            "Admin will announce results after match\n\n"
            "Good luck and play fair! 🎯"
        )
    
    @staticmethod
    def disclaimer() -> str:
        """Legal disclaimer message"""
        return (
            "⚖️ **LEGAL DISCLAIMER** ⚖️\n\n"
            "📋 **Terms & Conditions:**\n"
            "• This is a skill-based gaming tournament\n"
            "• Entry fee is for tournament organization\n"
            "• Participation is voluntary and at own risk\n"
            "• Admin reserves right to cancel/modify tournaments\n"
            "• Disputes will be resolved by admin decision\n\n"
            "🚫 **Age Restriction:**\n"
            "• Participants must be 18+ years old\n"
            "• Minors need parental consent\n"
            "• Verify age if requested\n\n"
            "💳 **Payment Policy:**\n"
            "• All transactions are secure\n"
            "• Entry fees are non-refundable\n"
            "• Prize money as per tournament terms\n\n"
            "📞 **Support:**\n"
            f"For any issues, contact: {Config.ADMIN_USERNAME}\n\n"
            "By participating, you agree to these terms. 📝"
        )
    
    @staticmethod
    def earnings_report(data: Dict[str, Any]) -> str:
        """Earnings report message for admin"""
        period_names = {
            "today": "Today",
            "thisweek": "This Week", 
            "thismonth": "This Month"
        }
        
        period_name = period_names.get(data.get("period", ""), "Unknown Period")
        
        return (
            f"📊 **EARNINGS REPORT - {period_name}** 📊\n\n"
            f"💰 **Total Earnings:** ₹{data.get('total_earnings', 0)}\n"
            f"🎮 **Tournaments:** {data.get('tournament_count', 0)}\n"
            f"👥 **Total Players:** {data.get('player_count', 0)}\n\n"
            f"📈 **Average per Tournament:** ₹{data.get('total_earnings', 0) // max(data.get('tournament_count', 1), 1)}\n"
            f"💵 **Average per Player:** ₹{data.get('total_earnings', 0) // max(data.get('player_count', 1), 1)}\n\n"
            "📅 **Report generated:** " + datetime.now().strftime("%d/%m/%Y %H:%M") + "\n\n"
            "Keep up the great work! 🚀"
        )
    
    # Notification messages
    NOTIFICATION_MESSAGES = {
        "morning": [
            "🌅 **Good Morning, Champions!** 🌅\n\nReady to conquer BGMI today? New tournaments await! ⚡",
            "☀️ **Rise and Grind!** ☀️\n\nMorning warriors, time to dominate the battleground! 🎮",
            "🌄 **New Day, New Victories!** 🌄\n\nCheck out today's tournaments and start winning! 🏆"
        ],
        "afternoon": [
            "🌞 **Good Afternoon, Gamers!** 🌞\n\nLunch break over? Time for some BGMI action! 🔥",
            "⏰ **Afternoon Gaming Session!** ⏰\n\nPerfect time to join a quick tournament! 🎯",
            "🌤️ **Midday Madness!** 🌤️\n\nAfternoon tournaments are heating up! Join now! 🚀"
        ],
        "evening": [
            "🌆 **Good Evening, Warriors!** 🌆\n\nPrime time for BGMI tournaments! Don't miss out! ⚡",
            "🌇 **Evening Battle Time!** 🌇\n\nBest tournaments happen in the evening! 🎮",
            "🌙 **Sunset Showdown!** 🌙\n\nEvening tournaments with amazing prizes! 🏆"
        ],
        "night": [
            "🌃 **Good Night, Champions!** 🌃\n\nLate night gaming sessions are the best! 🎯",
            "⭐ **Night Owl Tournament!** ⭐\n\nPerfect time for serious gamers! 🔥",
            "🌌 **Midnight Mayhem!** 🌌\n\nNight tournaments with double excitement! 🚀"
        ]
    }
    
    @staticmethod
    def get_notification_message(time_period: str) -> str:
        """Get random notification message for time period"""
        messages = Messages.NOTIFICATION_MESSAGES.get(time_period, ["Hello Champions! 🎮"])
        return random.choice(messages)
    
    @staticmethod
    def new_tournament_notification(tournament_data: Dict[str, Any]) -> str:
        """New tournament notification message"""
        return (
            "🚨 **NEW TOURNAMENT ALERT!** 🚨\n\n"
            f"🏆 **{tournament_data['name']}**\n"
            f"💰 Entry: ₹{tournament_data['entry_fee']} | Prize: ₹{tournament_data['prize_pool']}\n"
            f"📅 {tournament_data['date']} at {tournament_data['time']}\n\n"
            "⚡ **Register NOW before slots fill up!** ⚡\n"
            "Don't miss this epic battle! 🔥"
        )
