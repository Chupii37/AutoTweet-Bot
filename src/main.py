import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.core.logger import setup_logger
from src.core.scheduler import TweetScheduler
from src.core.twitter_client import TwitterClient

logger = setup_logger(__name__)

class AutoTweetBot:
    def __init__(self):
        self.scheduler = TweetScheduler()
        self.twitter_client = TwitterClient()
        self.is_running = False
    
    def start(self):
        """Start the bot"""
        try:
            logger.info("🚀 Starting Auto Tweet Bot...")
            
            self._validate_config()
            
            self._test_twitter_connection()
            
            logger.info("📅 Setting up tweet schedules...")
            self.scheduler.start()
            self.is_running = True
            
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            sys.exit(1)
    
    def _validate_config(self):
        """Validate configuration"""
        required_vars = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_SECRET'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
        
        logger.info("✅ Configuration validated")
    
    def _test_twitter_connection(self):
        """Test Twitter API connection"""
        try:
            user_info = self.twitter_client.get_user_info()
            if user_info:
                logger.info(f"✅ Connected to Twitter as: @{user_info['username']}")
                logger.info(f"   User ID: {user_info['id']}")
                logger.info(f"   Name: {user_info['name']}")
            else:
                raise Exception("Failed to get user info")
        except Exception as e:
            raise Exception(f"Twitter connection failed: {str(e)}")
    
    def stop(self):
        """Stop the bot"""
        if self.is_running:
            logger.info("🛑 Stopping Auto Tweet Bot...")
            self.scheduler.stop()
            self.is_running = False
            logger.info("👋 Bot stopped successfully")
    
    def run_once(self):
        """Run a single tweet (for testing)"""
        try:
            from src.content.content_manager import ContentManager
            content_manager = ContentManager()
            
            logger.info("Testing single tweet...")
            tweet_content = content_manager.generate_tweet()
            
            print(f"\nGenerated Tweet:\n{'='*50}")
            print(tweet_content)
            print(f"{'='*50}\n")
            
            if input("Post this tweet? (y/N): ").lower() == 'y':
                result = self.twitter_client.tweet(tweet_content)
                if result.get('success'):
                    logger.info("✅ Tweet posted successfully!")
                    content_manager.record_tweet(result.get('tweet_id'), tweet_content)
                else:
                    logger.error(f"❌ Failed to post tweet: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"Error in single tweet: {str(e)}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto Tweet Bot for X.com')
    parser.add_argument('--once', action='store_true', help='Post a single tweet and exit')
    parser.add_argument('--dry-run', action='store_true', help='Test without posting')
    parser.add_argument('--list-scheduled', action='store_true', help='List scheduled tweets')
    
    args = parser.parse_args()
    
    bot = AutoTweetBot()
    
    try:
        if args.once:
            bot.run_once()
        elif args.list_scheduled:
            scheduler = TweetScheduler()
            scheduler.schedule_tweets()
            jobs = scheduler.get_scheduled_jobs()
            
            print("\n📅 Scheduled Tweets:")
            print("="*50)
            for job in jobs:
                print(f"Job: {job['name']}")
                print(f"Next Run: {job['next_run']}")
                print(f"Trigger: {job['trigger']}")
                print("-"*50)
        else:
            bot.start()
    except KeyboardInterrupt:
        bot.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
