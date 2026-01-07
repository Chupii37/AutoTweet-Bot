import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json

def generate_random_string(length: int = 8) -> str:
    """Generate random string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def weighted_random_choice(items: List[Any], weights: List[float]) -> Any:
    """Weighted random choice"""
    if len(items) != len(weights):
        raise ValueError("Items and weights must have same length")
    
    total = sum(weights)
    r = random.uniform(0, total)
    
    cumulative = 0
    for item, weight in zip(items, weights):
        cumulative += weight
        if r <= cumulative:
            return item
    
    return items[-1]

def safe_json_load(filepath: str, default: Any = None) -> Any:
    """Safely load JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse string to datetime"""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
