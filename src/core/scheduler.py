import time
import random
import logging
from datetime import datetime
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
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone(ScheduleConfig.TIMEZONE))
        self.content_manager = ContentManager()
        self.twitter_client = TwitterClient()
        self.scheduled_times = []  # Store our scheduled times
        self.is_running = False
    
    def generate_random_schedule(self) -> List[Dict[str, Any]]:
        """Generate random schedule for tweets"""
        config = ScheduleConfig.SCHEDULE
        schedules = []
        
        for _ in range(config['count']):
            # Random day (0-6 = Monday-Sunday for APScheduler)
            random_day = random.choice(config['days'])
            
            # Random time within range
            start_hour = config['time_range']['start'].hour
            end_hour = config['time_range']['end'].hour
            
            random_hour = random.randint(start_hour, end_hour - 1)
            random_minute = random.randint(0, 59)
            
            schedules.append({
                'day_of_week': str(random_day),  # APScheduler expects string for cron
                'hour': random_hour,
                'minute': random_minute
            })
            
            # Store for logging
            day_names = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            self.scheduled_times.append({
                'day': day_names[random_day],
                'time': f"{random_hour:02d}:{random_minute:02d}"
            })
        
        logger.info(f"Generated {len(schedules)} random schedules")
        return schedules
    
    def schedule_tweets(self):
        """Schedule all tweets"""
        schedules = self.generate_random_schedule()
        
        for i, schedule_info in enumerate(schedules):
            # Create cron trigger - APScheduler cron format
            # Note: day_of_week: 0-6 or mon-sun
            trigger = CronTrigger(
                day_of_week=schedule_info['day_of_week'],
                hour=schedule_info['hour'],
                minute=schedule_info['minute'],
                timezone=pytz.timezone(ScheduleConfig.TIMEZONE)
            )
            
            # Add job to scheduler
            job = self.scheduler.add_job(
                func=self.post_scheduled_tweet,
                trigger=trigger,
                id=f'tweet_{i+1}',
                name=f'Scheduled Tweet {i+1}',
                replace_existing=True
            )
            
            # Log the scheduled time (from our stored info)
            if i < len(self.scheduled_times):
                scheduled = self.scheduled_times[i]
                logger.info(f"Scheduled tweet {i+1} for {scheduled['day']} at {scheduled['time']}")
    
    def post_scheduled_tweet(self):
        """Execute scheduled tweet"""
        try:
            logger.info("🎯 Executing scheduled tweet...")
            
            # Generate content
            tweet_content = self.content_manager.generate_tweet()
            
            # Check if dry run
            import os
            dry_run = os.getenv('DRY_RUN', 'False').lower() == 'true'
            
            if dry_run:
                logger.info(f"📝 DRY RUN - Would have tweeted: {tweet_content}")
                result = {
                    'success': True,
                    'dry_run': True,
                    'text': tweet_content
                }
            else:
                # Post tweet
                logger.info(f"📤 Posting tweet: {tweet_content[:80]}...")
                result = self.twitter_client.tweet(tweet_content)
            
            if result.get('success'):
                # Record tweet in history
                tweet_id = result.get('tweet_id', f"dry_run_{int(time.time())}")
                self.content_manager.record_tweet(tweet_id, tweet_content)
                logger.info("✅ Tweet processed successfully")
            else:
                logger.error(f"❌ Failed to process tweet: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"🔥 Error in scheduled tweet: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            logger.info("🔄 Starting tweet scheduler...")
            
            # Schedule tweets
            self.schedule_tweets()
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            # Log all scheduled times
            logger.info("📅 Scheduled tweet times:")
            for i, scheduled in enumerate(self.scheduled_times, 1):
                logger.info(f"  {i}. Every {scheduled['day']} at {scheduled['time']}")
            
            logger.info("✅ Tweet scheduler started successfully!")
            logger.info("🤖 Bot is now running. Press Ctrl+C to stop.")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                self.stop()
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            logger.info("🛑 Stopping tweet scheduler...")
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("✅ Tweet scheduler stopped")
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of scheduled jobs - simplified to avoid errors"""
        jobs = []
        for i, scheduled in enumerate(self.scheduled_times, 1):
            jobs.append({
                'id': f'tweet_{i}',
                'name': f'Scheduled Tweet {i}',
                'day': scheduled['day'],
                'time': scheduled['time'],
                'next_run': f"Every {scheduled['day']} at {scheduled['time']}"
            })
        return jobs
