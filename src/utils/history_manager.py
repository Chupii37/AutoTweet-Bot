"""
History manager for tweet history operations
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class HistoryManager:
    def __init__(self, history_file: str = None):
        if history_file is None:
            self.history_file = Path(__file__).parent.parent.parent / 'storage' / 'history.json'
        else:
            self.history_file = Path(history_file)
        
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Ensure history file exists"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            with open(self.history_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created history file: {self.history_file}")
    
    def add_tweet(self, tweet_data: Dict):
        """Add a tweet to history"""
        try:
            history = self.load_history()
            history.append(tweet_data)
            
            # Keep only last 1000 tweets
            if len(history) > 1000:
                history = history[-1000:]
            
            self.save_history(history)
            logger.debug(f"Added tweet to history: {tweet_data.get('id', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to add tweet to history: {str(e)}")
            return False
    
    def load_history(self) -> List[Dict]:
        """Load tweet history"""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            return history
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_history(self, history: List[Dict]):
        """Save tweet history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {str(e)}")
    
    def get_tweet_by_id(self, tweet_id: str) -> Optional[Dict]:
        """Get tweet by ID"""
        history = self.load_history()
        for tweet in history:
            if tweet.get('id') == tweet_id:
                return tweet
        return None
    
    def get_recent_tweets(self, limit: int = 10) -> List[Dict]:
        """Get most recent tweets"""
        history = self.load_history()
        return history[-limit:] if history else []
    
    def get_tweets_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Get tweets by category"""
        history = self.load_history()
        filtered = [t for t in history if t.get('category') == category]
        return filtered[-limit:] if filtered else []
    
    def get_tweets_by_date(self, start_date: datetime, end_date: datetime = None) -> List[Dict]:
        """Get tweets within date range"""
        if end_date is None:
            end_date = datetime.now()
        
        history = self.load_history()
        filtered = []
        
        for tweet in history:
            try:
                tweet_date = datetime.fromisoformat(tweet.get('timestamp').replace('Z', '+00:00'))
                if start_date <= tweet_date <= end_date:
                    filtered.append(tweet)
            except (ValueError, AttributeError):
                continue
        
        return filtered
    
    def get_statistics(self) -> Dict:
        """Get statistics from history"""
        history = self.load_history()
        
        if not history:
            return {
                'total_tweets': 0,
                'successful_tweets': 0,
                'failed_tweets': 0,
                'success_rate': 0.0,
                'total_impressions': 0,
                'total_engagements': 0,
                'categories': {}
            }
        
        total = len(history)
        successful = sum(1 for t in history if t.get('success'))
        failed = total - successful
        
        # Calculate impressions and engagements
        total_impressions = sum(t.get('impressions', 0) for t in history)
        total_engagements = sum(
            t.get('likes', 0) + t.get('retweets', 0) + t.get('replies', 0) 
            for t in history
        )
        
        # Category distribution
        categories = {}
        for tweet in history:
            cat = tweet.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_tweets': total,
            'successful_tweets': successful,
            'failed_tweets': failed,
            'success_rate': successful / total if total > 0 else 0.0,
            'total_impressions': total_impressions,
            'total_engagements': total_engagements,
            'engagement_rate': total_engagements / total_impressions if total_impressions > 0 else 0.0,
            'categories': categories,
            'last_updated': datetime.now().isoformat()
        }
    
    def cleanup_old_tweets(self, days_to_keep: int = 90):
        """Remove tweets older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        history = self.load_history()
        initial_count = len(history)
        
        filtered = []
        for tweet in history:
            try:
                tweet_date = datetime.fromisoformat(tweet.get('timestamp').replace('Z', '+00:00'))
                if tweet_date >= cutoff_date:
                    filtered.append(tweet)
            except (ValueError, AttributeError):
                # Keep if we can't parse date
                filtered.append(tweet)
        
        self.save_history(filtered)
        removed = initial_count - len(filtered)
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} tweets older than {days_to_keep} days")
        
        return removed
    
    def export_history(self, export_format: str = 'json', filepath: str = None) -> bool:
        """Export history to file"""
        history = self.load_history()
        
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = self.history_file.parent / f'history_export_{timestamp}.{export_format}'
        
        try:
            if export_format.lower() == 'json':
                with open(filepath, 'w') as f:
                    json.dump(history, f, indent=2)
            elif export_format.lower() == 'csv':
                import csv
                with open(filepath, 'w', newline='') as f:
                    if history:
                        writer = csv.DictWriter(f, fieldnames=history[0].keys())
                        writer.writeheader()
                        writer.writerows(history)
            else:
                logger.error(f"Unsupported export format: {export_format}")
                return False
            
            logger.info(f"History exported to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export history: {str(e)}")
            return False
