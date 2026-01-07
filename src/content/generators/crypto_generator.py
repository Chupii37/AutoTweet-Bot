import json
import random
from pathlib import Path
from typing import List

class CryptoGenerator:
    def __init__(self):
        data_file = Path(__file__).parent.parent / 'data' / 'crypto_topics.json'
        with open(data_file, 'r') as f:
            self.data = json.load(f)
    
    def generate(self) -> str:
        """Generate a crypto-related tweet"""
        topic = random.choice(self.data['topics'])
        template = random.choice(self.data['templates'])
        hashtag = random.choice(self.data['hashtags'])
        
        tweet = template.replace('{topic}', topic).replace('{hashtag}', hashtag)
        
        additional_hashtags = self._get_random_hashtags(3)
        tweet += ' ' + ' '.join(additional_hashtags)
        
        return tweet.strip()
    
    def _get_random_hashtags(self, count: int = 3) -> List[str]:
        """Get random hashtags"""
        hashtags = self.data['hashtags'].copy()
        random.shuffle(hashtags)
        return hashtags[:min(count, len(hashtags))]
