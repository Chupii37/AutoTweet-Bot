import json
import random
from pathlib import Path
from typing import Dict, List

class FunnyGenerator:
    def __init__(self):
        data_file = Path(__file__).parent.parent / 'data' / 'jokes.json'
        with open(data_file, 'r') as f:
            self.jokes = json.load(f)
        
        self.hashtag_map = {
            'programming': ['#Programming', '#TechJokes', '#DeveloperHumor', '#Coding'],
            'general': ['#Funny', '#Joke', '#Laugh', '#Humor'],
            'puns': ['#Puns', '#Wordplay', '#DadJokes'],
            'crypto': ['#CryptoHumor', '#BitcoinJokes', '#BlockchainJokes']
        }
    
    def generate(self) -> str:
        """Generate a funny tweet"""
        categories = list(self.jokes.keys())
        category = random.choice(categories)
        
        joke = random.choice(self.jokes[category])
        
        hashtags = self.hashtag_map.get(category, ['#Funny', '#Humor'])
        random.shuffle(hashtags)
        selected_hashtags = hashtags[:random.randint(1, 3)]
        
        return f"{joke}\n\n{' '.join(selected_hashtags)}"
