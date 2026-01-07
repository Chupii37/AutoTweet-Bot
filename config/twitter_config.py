import os
from dotenv import load_dotenv

load_dotenv()

class TwitterConfig:
    API_KEY = os.getenv('TWITTER_API_KEY')
    API_SECRET = os.getenv('TWITTER_API_SECRET')
    ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
    BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    
    RATE_LIMIT = {
        'max_requests': 50,
        'per_minutes': 15
    }
    
    @classmethod
    def validate(cls):
        required_vars = ['API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_SECRET']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing Twitter configuration: {', '.join(missing)}")
        
        return True
