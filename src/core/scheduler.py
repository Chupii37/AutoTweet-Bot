import schedule
import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from config.schedule_config import ScheduleConfig
from src.content.content_manager import ContentManager
from src.core.twitter_client import TwitterClient
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class TweetScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=pytz.UTC)
        self.content_manager = ContentManager()
        self.twitter_client = TwitterClient()
        self.scheduled_jobs = []
        self.is_running = False
    
    def generate_random_schedule(self) -> List[Dict[str, Any]]:
        """Generate random schedule for tweets"""
        config = ScheduleConfig.SCHEDULE
        schedules = []
        
        for _ in range(config['count']):
            random_day = random.choice(config['days'])
            
            start_hour = config['time_range']['start'].hour
            end_hour = config['time_range']['end'].hour
            
            random_hour = random.randint(start_hour, end_hour - 1)
            random_minute = random.randint(0, 59)
            
            schedules.append({
                'day_of_week': random_day,
                'hour': random_hour,
                'minute': random_minute
            })
        
        logger.info(f"Generated {len(schedules)} random schedules")
        return schedules
    
    def schedule_tweets(self):
        """Schedule all tweets"""
        schedules = self.generate_random_schedule()
        
        for i, schedule_info in enumerate(schedules):
            trigger = CronTrigger(
                day_of_week=schedule_info['day_of_week'],
                hour=schedule_info['hour'],
                minute=schedule_info['minute'],
                timezone=pytz.timezone(ScheduleConfig.TIMEZONE)
            )
            
            job = self.scheduler.add_job(
                self.post_scheduled_tweet,
                trigger=trigger,
                id=f'tweet_{i+1}',
                name=f'Scheduled Tweet {i+1}'
            )
            
            self.scheduled_jobs.append(job)
            
            next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Scheduled tweet {i+1} for: {next_run}")
    
    def post_scheduled_tweet(self):
        """Execute scheduled tweet"""
        try:
            logger.info("Executing scheduled tweet...")
            
            tweet_content = self.content_manager.generate_tweet()
            
            result = self.twitter_client.tweet(tweet_content)
            
            if result.get('success'):
                self.content_manager.record_tweet(
                    result.get('tweet_id'),
                    tweet_content
                )
                logger.info("Tweet posted successfully")
            else:
                logger.error(f"Failed to post tweet: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in scheduled tweet: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.schedule_tweets()
            self.scheduler.start()
            self.is_running = True
            logger.info("Tweet scheduler started")
            
            try:
                while True:
                    time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                self.stop()
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Tweet scheduler stopped")
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time,
                'trigger': str(job.trigger)
            })
        return jobs
