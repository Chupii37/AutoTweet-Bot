import json
import random
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from config.schedule_config import ScheduleConfig
from src.content.generators.crypto_generator import CryptoGenerator
from src.content.generators.funny_generator import FunnyGenerator
from src.content.generators.finance_generator import FinanceGenerator
from src.content.generators.social_generator import SocialGenerator

logger = logging.getLogger(__name__)

class ContentManager:
    def __init__(self):
        self.generators = {
            'crypto': CryptoGenerator(),
            'funny': FunnyGenerator(),
            'finance': FinanceGenerator(),
            'social': SocialGenerator(),
            'sociology': SocialGenerator()  
        }
        
        self.history_file = Path(__file__).parent.parent.parent / 'storage' / 'history.json'
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Ensure history file exists"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def generate_tweet(self) -> str:
        """Generate a tweet with weighted random category selection"""
        categories = list(ScheduleConfig.CATEGORIES.keys())
        weights = list(ScheduleConfig.CATEGORIES.values())
        
        selected_category = random.choices(categories, weights=weights, k=1)[0]
        
        logger.info(f"Generating {selected_category} tweet...")
        
        generator = self.generators.get(selected_category)
        if not generator:
            generator = self.generators['crypto']
        
        tweet_content = generator.generate()
        
        tweet_content = self._trim_tweet(tweet_content)
        
        return tweet_content
    
    def _trim_tweet(self, tweet: str, max_length: int = 280) -> str:
        """Trim tweet to fit within character limit"""
        if len(tweet) <= max_length:
            return tweet
        
        import re
        hashtags = re.findall(r'#\w+', tweet)
        tweet_without_hashtags = re.sub(r'#\w+', '', tweet).strip()
        
        hashtags_text = ' '.join(hashtags) if hashtags else ''
        
        if len(tweet_without_hashtags) + len(hashtags_text) + 1 <= max_length:
            return f"{tweet_without_hashtags} {hashtags_text}".strip()
        
        available_length = max_length - len(hashtags_text) - 1
        
        if available_length > 20:
            trimmed_text = tweet_without_hashtags[:available_length - 3] + '...'
            return f"{trimmed_text} {hashtags_text}".strip()
        
        return tweet[:max_length - 3] + '...'
    
    def record_tweet(self, tweet_id: str, content: str):
        """Record tweet in history"""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            tweet_record = {
                'id': tweet_id,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'category': self._detect_category(content)
            }
            
            history.append(tweet_record)
            
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info(f"Tweet recorded: {tweet_id}")
            
        except Exception as e:
            logger.error(f"Failed to record tweet: {str(e)}")
    
    def _detect_category(self, content: str) -> str:
        """Detect category from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['crypto', 'bitcoin', 'ethereum', 'blockchain']):
            return 'crypto'
        elif any(word in content_lower for word in ['joke', 'funny', 'humor', 'laugh']):
            return 'funny'
        elif any(word in content_lower for word in ['finance', 'invest', 'money', 'stock']):
            return 'finance'
        elif any(word in content_lower for word in ['social', 'sociology', 'society', 'community']):
            return 'social'
        
        return 'general'
    
    def get_tweet_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tweet history"""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            return history[-limit:]
        except Exception as e:
            logger.error(f"Failed to get tweet history: {str(e)}")
            return []
