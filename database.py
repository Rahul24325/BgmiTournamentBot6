"""
Database operations for the BGMI Tournament Bot
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

from .config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def init_database(self):
        """Initialize database connection"""
        try:
            self.client = AsyncIOMotorClient(Config.MONGODB_URI)
            self.db = self.client[Config.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            await self.db.users.create_index("user_id", unique=True)
            await self.db.users.create_index("username")
            
            # Tournaments collection indexes
            await self.db.tournaments.create_index("tournament_id", unique=True)
            await self.db.tournaments.create_index("status")
            await self.db.tournaments.create_index("date")
            
            # Payments collection indexes
            await self.db.payments.create_index([("user_id", 1), ("tournament_id", 1)])
            await self.db.payments.create_index("status")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # User Operations
    async def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Add or update user in database"""
        try:
            user_data["last_activity"] = datetime.utcnow()
            user_data["created_at"] = datetime.utcnow()
            
            await self.db.users.update_one(
                {"user_id": user_data["user_id"]},
                {"$set": user_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            return await self.db.users.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def get_all_active_users(self) -> List[Dict[str, Any]]:
        """Get all active users for notifications"""
        try:
            # Users active in last 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            cursor = self.db.users.find({"last_activity": {"$gte": cutoff_date}})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    # Tournament Operations
    async def create_tournament(self, tournament_data: Dict[str, Any]) -> str:
        """Create a new tournament"""
        try:
            tournament_id = f"tournament_{int(datetime.utcnow().timestamp())}"
            tournament_data["tournament_id"] = tournament_id
            tournament_data["created_at"] = datetime.utcnow()
            tournament_data["status"] = "active"
            tournament_data["participants"] = []
            tournament_data["confirmed_players"] = []
            
            await self.db.tournaments.insert_one(tournament_data)
            return tournament_id
        except Exception as e:
            logger.error(f"Error creating tournament: {e}")
            return ""
    
    async def get_tournament(self, tournament_id: str) -> Optional[Dict[str, Any]]:
        """Get tournament by ID"""
        try:
            return await self.db.tournaments.find_one({"tournament_id": tournament_id})
        except Exception as e:
            logger.error(f"Error getting tournament: {e}")
            return None
    
    async def get_active_tournaments(self) -> List[Dict[str, Any]]:
        """Get all active tournaments"""
        try:
            cursor = self.db.tournaments.find({"status": "active"})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting active tournaments: {e}")
            return []
    
    async def add_participant(self, tournament_id: str, user_id: int) -> bool:
        """Add participant to tournament"""
        try:
            result = await self.db.tournaments.update_one(
                {"tournament_id": tournament_id},
                {"$addToSet": {"participants": user_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding participant: {e}")
            return False
    
    async def confirm_player(self, tournament_id: str, user_id: int) -> bool:
        """Confirm player payment for tournament"""
        try:
            result = await self.db.tournaments.update_one(
                {"tournament_id": tournament_id},
                {"$addToSet": {"confirmed_players": user_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error confirming player: {e}")
            return False
    
    async def decline_player(self, tournament_id: str, user_id: int) -> bool:
        """Decline player payment for tournament"""
        try:
            result = await self.db.tournaments.update_one(
                {"tournament_id": tournament_id},
                {"$pull": {"participants": user_id, "confirmed_players": user_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error declining player: {e}")
            return False
    
    async def close_tournament(self, tournament_id: str) -> bool:
        """Close tournament and mark as completed"""
        try:
            result = await self.db.tournaments.update_one(
                {"tournament_id": tournament_id},
                {"$set": {"status": "completed", "completed_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error closing tournament: {e}")
            return False
    
    async def delete_tournament(self, tournament_id: str) -> bool:
        """Delete tournament completely"""
        try:
            result = await self.db.tournaments.delete_one({"tournament_id": tournament_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting tournament: {e}")
            return False
    
    # Payment Operations
    async def add_payment(self, payment_data: Dict[str, Any]) -> bool:
        """Add payment record"""
        try:
            payment_data["created_at"] = datetime.utcnow()
            payment_data["status"] = "pending"
            
            await self.db.payments.insert_one(payment_data)
            return True
        except Exception as e:
            logger.error(f"Error adding payment: {e}")
            return False
    
    async def confirm_payment(self, user_id: int, tournament_id: str) -> bool:
        """Confirm user payment"""
        try:
            result = await self.db.payments.update_one(
                {"user_id": user_id, "tournament_id": tournament_id},
                {"$set": {"status": "confirmed", "confirmed_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            return False
    
    async def decline_payment(self, user_id: int, tournament_id: str) -> bool:
        """Decline user payment"""
        try:
            result = await self.db.payments.update_one(
                {"user_id": user_id, "tournament_id": tournament_id},
                {"$set": {"status": "declined", "declined_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error declining payment: {e}")
            return False
    
    # Earnings Operations
    async def get_earnings(self, period: str) -> Dict[str, Any]:
        """Get earnings for specified period (today, thisweek, thismonth)"""
        try:
            now = datetime.utcnow()
            
            if period == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "thisweek":
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "thismonth":
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                return {"total_earnings": 0, "tournament_count": 0, "player_count": 0}
            
            # Get tournaments in date range
            tournaments = await self.db.tournaments.find({
                "created_at": {"$gte": start_date},
                "status": {"$in": ["active", "completed"]}
            }).to_list(length=None)
            
            total_earnings = 0
            total_players = 0
            
            for tournament in tournaments:
                confirmed_count = len(tournament.get("confirmed_players", []))
                entry_fee = tournament.get("entry_fee", 0)
                total_earnings += confirmed_count * entry_fee
                total_players += confirmed_count
            
            return {
                "total_earnings": total_earnings,
                "tournament_count": len(tournaments),
                "player_count": total_players,
                "period": period
            }
        except Exception as e:
            logger.error(f"Error getting earnings: {e}")
            return {"total_earnings": 0, "tournament_count": 0, "player_count": 0}

# Global database instance
db = Database()

async def init_database():
    """Initialize database connection"""
    await db.init_database()
