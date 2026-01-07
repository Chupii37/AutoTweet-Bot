"""
Configuration package for Auto Tweet Bot
"""

from .twitter_config import TwitterConfig
from .schedule_config import ScheduleConfig

__all__ = ['TwitterConfig', 'ScheduleConfig']
__version__ = '1.0.0'
