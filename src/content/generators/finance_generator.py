import json
import random
from pathlib import Path
from typing import Dict, List

class FinanceGenerator:
    def __init__(self):
        data_file = Path(__file__).parent.parent / 'data' / 'finance_quotes.json'
        with open(data_file, 'r') as f:
            self.data = json.load(f)
    
    def generate(self) -> str:
        """Generate a finance-related tweet"""
        rand_val = random.random()
        
        if rand_val < 0.4:
            quote = random.choice(self.data['quotes'])
            return f"\"{quote['text']}\" — {quote['author']}\n\n#Finance #Investing #Money"
        
        elif rand_val < 0.7:
            tip = random.choice(self.data['tips'])
            return f"💰 Financial Tip: {tip}\n\n#FinancialFreedom #MoneyTips #PersonalFinance"
        
        else:
            stat = random.choice(self.data['statistics'])
            return f"📊 Did you know? {stat}\n\n#FinanceFacts #Economics #Investing"
