import json
import random
from pathlib import Path
from typing import List

class SocialGenerator:
    def __init__(self):
        data_file = Path(__file__).parent.parent / 'data' / 'social_topics.json'
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        self.discussion_starters = [
            "What's the most positive change you've seen in social media lately?",
            "How has technology changed the way we form communities?",
            "What's one social norm you wish would change?",
            "How do you balance online and offline social interactions?",
            "What role should social media play in society?",
            "How can we build better online communities?"
        ]
    
    def generate(self) -> str:
        """Generate a social/sociology tweet"""
        rand_val = random.random()
        
        if rand_val < 0.3:
            topic = random.choice(self.data['topics'])
            question = random.choice(self.data['questions'])
            return f"{topic}\n\n{question}\n\n#SocialMedia #Society #Discussion"
        
        elif rand_val < 0.6:
            insight = random.choice(self.data['insights'])
            return f"🧠 Social Insight: {insight}\n\n#Sociology #HumanBehavior #Psychology"
        
        else:
            starter = random.choice(self.discussion_starters)
            return f"💭 Discussion: {starter}\n\n#SocialDiscussion #Community #Thoughts"
