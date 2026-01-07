from datetime import time

class ScheduleConfig:
    SCHEDULE = {
        'frequency': 'week',
        'count': 2,
        'time_range': {
            'start': time(9, 0),   
            'end': time(21, 0)     
        },
        'days': [0, 1, 2, 3, 4, 5, 6]
    }
    
    CATEGORIES = {
        'crypto': 0.25,
        'funny': 0.20,
        'finance': 0.20,
        'social': 0.20,
        'sociology': 0.15
    }
    
    TIMEZONE = 'UTC'
