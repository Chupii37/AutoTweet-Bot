import tweepy
import logging
from typing import Optional, Dict, Any
from config.twitter_config import TwitterConfig

logger = logging.getLogger(__name__)

class TwitterClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TwitterClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Twitter client"""
        TwitterConfig.validate()
        
        self.auth = tweepy.OAuth1UserHandler(
            TwitterConfig.API_KEY,
            TwitterConfig.API_SECRET,
            TwitterConfig.ACCESS_TOKEN,
            TwitterConfig.ACCESS_SECRET
        )
        
        self.client = tweepy.Client(
            bearer_token=TwitterConfig.BEARER_TOKEN,
            consumer_key=TwitterConfig.API_KEY,
            consumer_secret=TwitterConfig.API_SECRET,
            access_token=TwitterConfig.ACCESS_TOKEN,
            access_token_secret=TwitterConfig.ACCESS_SECRET,
            wait_on_rate_limit=True
        )
        
        self.api_v1 = tweepy.API(self.auth)
        
        logger.info("Twitter client initialized")
    
    def tweet(self, content: str, **kwargs) -> Dict[str, Any]:
        """Post a tweet"""
        try:
            logger.info(f"Posting tweet: {content[:50]}...")
            
            if kwargs.get('dry_run', False):
                logger.info(f"DRY RUN: Would have tweeted: {content}")
                return {
                    'success': True,
                    'dry_run': True,
                    'text': content
                }
            
            response = self.client.create_tweet(text=content)
            
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"Tweet posted successfully: {tweet_id}")
                
                return {
                    'success': True,
                    'tweet_id': tweet_id,
                    'text': content
                }
            else:
                raise Exception("No response data from Twitter API")
                
        except tweepy.TweepyException as e:
            logger.error(f"Failed to post tweet: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error posting tweet: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_media(self, file_path: str, media_type: str = 'image/jpeg') -> Optional[str]:
        """Upload media to Twitter"""
        try:
            media = self.api_v1.media_upload(filename=file_path)
            logger.info(f"Media uploaded: {media.media_id}")
            return media.media_id
        except Exception as e:
            logger.error(f"Failed to upload media: {str(e)}")
            return None
    
    def get_tweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Get tweet details"""
        try:
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['created_at', 'public_metrics']
            )
            return tweet.data
        except Exception as e:
            logger.error(f"Failed to get tweet: {str(e)}")
            return None
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get authenticated user info"""
        try:
            user = self.client.get_me(user_fields=['public_metrics'])
            return user.data
        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            return None
