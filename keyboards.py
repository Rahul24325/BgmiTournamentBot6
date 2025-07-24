"""
Inline keyboards for the BGMI Tournament Bot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    @staticmethod
    def main_menu():
        """Main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🎮 Join Tournament", callback_data="join_tournament")],
            [InlineKeyboardButton("📋 Tournament Rules", callback_data="rules")],
            [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/Officialbgmi24")],
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/KyaTereSquadMeinDumHai")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def tournament_join(tournament_id: str):
        """Tournament join keyboard"""
        keyboard = [
            [InlineKeyboardButton("🎯 Join Tournament", callback_data=f"join_{tournament_id}")],
            [InlineKeyboardButton("📋 Rules & Info", callback_data="rules")],
            [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/Officialbgmi24")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def payment_confirmation():
        """Payment confirmation keyboard"""
        keyboard = [
            [InlineKeyboardButton("✅ Payment Done", callback_data="payment_done")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")],
            [InlineKeyboardButton("❓ Need Help?", url="https://t.me/Officialbgmi24")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_menu():
        """Admin menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🏆 Solo Tournament", callback_data="create_solo"),
                InlineKeyboardButton("👥 Squad Tournament", callback_data="create_squad")
            ],
            [
                InlineKeyboardButton("📊 List Players", callback_data="list_players"),
                InlineKeyboardButton("💰 Earnings", callback_data="earnings_menu")
            ],
            [
                InlineKeyboardButton("🏁 Declare Winners", callback_data="declare_winners"),
                InlineKeyboardButton("🗑️ Clear Tournaments", callback_data="clear_tournaments")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def earnings_menu():
        """Earnings menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("📅 Today", callback_data="earnings_today")],
            [InlineKeyboardButton("📆 This Week", callback_data="earnings_week")],
            [InlineKeyboardButton("📈 This Month", callback_data="earnings_month")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def tournament_management(tournament_id: str):
        """Tournament management keyboard"""
        keyboard = [
            [InlineKeyboardButton("📋 List Players", callback_data=f"list_{tournament_id}")],
            [InlineKeyboardButton("📤 Send Room Details", callback_data=f"room_{tournament_id}")],
            [InlineKeyboardButton("🏁 Declare Winners", callback_data=f"winners_{tournament_id}")],
            [InlineKeyboardButton("🗑️ Delete Tournament", callback_data=f"delete_{tournament_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_action(action: str, data: str):
        """Confirmation keyboard for actions"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{data}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def rules_navigation():
        """Rules and information navigation"""
        keyboard = [
            [InlineKeyboardButton("🎮 Tournament Rules", callback_data="tournament_rules")],
            [InlineKeyboardButton("💰 Payment Info", callback_data="payment_info")],
            [InlineKeyboardButton("⚖️ Disclaimer", callback_data="disclaimer")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_button():
        """Simple back button"""
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def tournament_type_selection():
        """Tournament type selection keyboard"""
        keyboard = [
            [InlineKeyboardButton("🏆 Solo Tournament", callback_data="create_solo")],
            [InlineKeyboardButton("👥 Squad Tournament", callback_data="create_squad")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_creation")]
        ]
        return InlineKeyboardMarkup(keyboard)
