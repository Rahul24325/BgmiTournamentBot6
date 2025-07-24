"""
AI Service for intelligent tournament suggestions and analysis
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional
import aiohttp

from .config import Config

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = Config.AI_API_KEY
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    async def make_ai_request(self, prompt: str, max_tokens: int = 150) -> Optional[str]:
        """Make request to AI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI assistant specialized in BGMI tournament management and gaming analytics. Provide concise, practical suggestions."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content'].strip()
                    else:
                        logger.error(f"AI API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error making AI request: {e}")
            return None
    
    async def suggest_prize_pool(self, entry_fee: int) -> int:
        """Suggest optimal prize pool based on entry fee"""
        try:
            prompt = f"""
            For a BGMI tournament with entry fee of ₹{entry_fee}, suggest an optimal prize pool amount.
            Consider:
            - Attractive for players
            - Profitable for organizer
            - Industry standards
            - Player psychology
            
            Just return the number amount, no explanation.
            """
            
            response = await self.make_ai_request(prompt, 50)
            if response:
                # Extract number from response
                import re
                numbers = re.findall(r'\d+', response)
                if numbers:
                    return int(numbers[0])
            
            # Fallback calculation
            return entry_fee * 8  # 8x entry fee as default
            
        except Exception as e:
            logger.error(f"Error suggesting prize pool: {e}")
            return entry_fee * 8
    
    async def analyze_tournament_performance(self, tournament_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tournament performance and provide insights"""
        try:
            participants = len(tournament_data.get('confirmed_players', []))
            entry_fee = tournament_data.get('entry_fee', 0)
            prize_pool = tournament_data.get('prize_pool', 0)
            total_revenue = participants * entry_fee
            profit = total_revenue - prize_pool
            
            prompt = f"""
            Analyze this BGMI tournament performance:
            - Participants: {participants}
            - Entry Fee: ₹{entry_fee}
            - Prize Pool: ₹{prize_pool}
            - Total Revenue: ₹{total_revenue}
            - Profit: ₹{profit}
            
            Provide insights on:
            1. Performance rating (1-10)
            2. Profit margin assessment
            3. Player engagement level
            4. Suggestions for improvement
            
            Format as JSON with keys: rating, profit_margin, engagement, suggestions
            """
            
            response = await self.make_ai_request(prompt, 200)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
            
            # Fallback analysis
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
            rating = min(10, max(1, participants // 2))  # Simple rating based on participants
            
            return {
                "rating": rating,
                "profit_margin": f"{profit_margin:.1f}%",
                "engagement": "Good" if participants >= 10 else "Average",
                "suggestions": [
                    "Consider adjusting entry fee based on demand",
                    "Optimize prize distribution for better attraction",
                    "Promote tournament in gaming communities"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing tournament performance: {e}")
            return {"error": "Analysis failed"}
    
    async def suggest_tournament_timing(self) -> Dict[str, Any]:
        """Suggest optimal tournament timing"""
        try:
            prompt = """
            Suggest optimal timing for BGMI tournaments in India considering:
            - Player availability
            - Peak gaming hours
            - Weekend vs weekday preferences
            - School/work schedules
            
            Provide suggestions for:
            1. Best day of week
            2. Optimal time slots
            3. Duration recommendations
            
            Format as JSON with keys: best_day, time_slots, duration
            """
            
            response = await self.make_ai_request(prompt, 150)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
            
            # Fallback suggestions
            return {
                "best_day": "Saturday/Sunday",
                "time_slots": ["16:00-18:00", "20:00-22:00"],
                "duration": "1-2 hours"
            }
            
        except Exception as e:
            logger.error(f"Error suggesting tournament timing: {e}")
            return {"error": "Timing suggestion failed"}
    
    async def generate_tournament_name(self, tournament_type: str, theme: Optional[str] = None) -> str:
        """Generate creative tournament name"""
        try:
            prompt = f"""
            Generate a creative and exciting name for a BGMI {tournament_type} tournament.
            {f'Theme: {theme}' if theme else ''}
            
            Requirements:
            - Catchy and memorable
            - Gaming-related
            - Professional yet exciting
            - Hindi/English mix acceptable
            
            Just return the name, no explanation.
            """
            
            response = await self.make_ai_request(prompt, 50)
            if response:
                return response.strip('"').strip("'")
            
            # Fallback names
            fallback_names = {
                "Solo": "Solo Supremacy Championship",
                "Squad": "Squad Showdown Battle",
            }
            return fallback_names.get(tournament_type, "BGMI Championship")
            
        except Exception as e:
            logger.error(f"Error generating tournament name: {e}")
            return f"{tournament_type} Championship"
    
    async def predict_participation(self, tournament_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict tournament participation based on historical data"""
        try:
            entry_fee = tournament_data.get('entry_fee', 0)
            prize_pool = tournament_data.get('prize_pool', 0)
            tournament_type = tournament_data.get('type', 'Solo')
            
            prompt = f"""
            Predict participation for BGMI tournament:
            - Type: {tournament_type}
            - Entry Fee: ₹{entry_fee}
            - Prize Pool: ₹{prize_pool}
            - Prize to Entry Ratio: {prize_pool / entry_fee if entry_fee > 0 else 0:.1f}x
            
            Based on gaming market trends, provide:
            1. Expected participants (number)
            2. Confidence level (High/Medium/Low)
            3. Key factors affecting participation
            
            Format as JSON with keys: expected_participants, confidence, factors
            """
            
            response = await self.make_ai_request(prompt, 150)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
            
            # Fallback prediction
            base_participants = 15 if tournament_type == "Solo" else 8
            fee_factor = max(0.5, min(2.0, 50 / entry_fee)) if entry_fee > 0 else 1
            expected = int(base_participants * fee_factor)
            
            return {
                "expected_participants": expected,
                "confidence": "Medium",
                "factors": ["Entry fee", "Prize pool", "Tournament timing"]
            }
            
        except Exception as e:
            logger.error(f"Error predicting participation: {e}")
            return {"error": "Prediction failed"}
    
    async def optimize_pricing_strategy(self, current_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest pricing optimization based on performance"""
        try:
            prompt = f"""
            Based on tournament performance data:
            {json.dumps(current_performance, indent=2)}
            
            Suggest pricing optimization strategy:
            1. Recommended entry fee adjustments
            2. Prize pool optimization
            3. Profit margin improvements
            4. Player retention strategies
            
            Format as JSON with keys: entry_fee_suggestion, prize_pool_suggestion, strategies
            """
            
            response = await self.make_ai_request(prompt, 200)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
            
            # Fallback optimization
            return {
                "entry_fee_suggestion": "Consider A/B testing different price points",
                "prize_pool_suggestion": "Maintain 70-80% of revenue as prize pool",
                "strategies": [
                    "Introduce early bird discounts",
                    "Create loyalty programs for regular players",
                    "Optimize prize distribution structure"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing pricing: {e}")
            return {"error": "Optimization failed"}
