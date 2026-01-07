"""
Auto Tweet Bot for X.com
Automatically posts tweets 2x a week with various content categories
"""

__version__ = '1.0.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'

# Package metadata
__description__ = 'Auto tweet bot for X.com with scheduled posting'
__url__ = 'https://github.com/yourusername/auto-tweet-bot'
__license__ = 'MIT'

# Export main classes
from .main import AutoTweetBot

__all__ = ['AutoTweetBot']
