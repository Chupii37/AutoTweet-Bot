"""
Validation utilities for Auto Tweet Bot
Validates environment variables, tweet content, and configurations
"""

import os
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, time
import json

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class ContentValidator:
    """Validates tweet content for safety and compliance"""
    
    # Common blocked words/phrases (can be loaded from file)
    DEFAULT_BLOCKED_WORDS = [
        'hate', 'kill', 'murder', 'terrorist', 'bomb',
        'scam', 'fraud', 'cheat', 'steal',
        'sucker', 'idiot', 'stupid', 'moron',
        # Add more as needed
    ]
    
    # Twitter reserved words/characters
    RESERVED_HASHTAGS = [
        'twitter', 'admin', 'support', 'help',
        'api', 'oauth', 'security'
    ]
    
    def __init__(self, blocked_words_file: Optional[str] = None):
        self.blocked_words = self.DEFAULT_BLOCKED_WORDS.copy()
        
        # Load additional blocked words from file if provided
        if blocked_words_file and os.path.exists(blocked_words_file):
            try:
                with open(blocked_words_file, 'r') as f:
                    additional_words = [line.strip() for line in f if line.strip()]
                    self.blocked_words.extend(additional_words)
            except Exception as e:
                logger.warning(f"Failed to load blocked words file: {str(e)}")
    
    def validate_tweet_content(self, content: str, max_length: int = 280) -> Dict[str, any]:
        """
        Validate tweet content for safety and compliance
        
        Args:
            content: Tweet content to validate
            max_length: Maximum allowed tweet length
            
        Returns:
            Dict with validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check length
        if len(content) > max_length:
            validation_results['is_valid'] = False
            validation_results['errors'].append(
                f"Tweet exceeds {max_length} characters ({len(content)} chars)"
            )
        
        # Check for blocked words
        profane_check = self.is_profane_content(content)
        if profane_check['has_profane']:
            validation_results['is_valid'] = False
            validation_results['errors'].append(
                f"Contains inappropriate content: {', '.join(profane_check['found_words'])}"
            )
        
        # Check for excessive hashtags (Twitter recommends max 2-3)
        hashtags = self.extract_hashtags(content)
        if len(hashtags) > 5:
            validation_results['warnings'].append(
                f"Too many hashtags ({len(hashtags)}). Twitter recommends 2-3 hashtags max."
            )
        
        # Check for reserved hashtags
        reserved_used = [ht for ht in hashtags if ht.lower() in self.RESERVED_HASHTAGS]
        if reserved_used:
            validation_results['warnings'].append(
                f"Using reserved hashtags: {', '.join(reserved_used)}"
            )
        
        # Check for excessive mentions
        mentions = self.extract_mentions(content)
        if len(mentions) > 3:
            validation_results['warnings'].append(
                f"Too many mentions ({len(mentions)}). This may trigger spam filters."
            )
        
        # Check for URLs
        urls = self.extract_urls(content)
        if len(urls) > 2:
            validation_results['warnings'].append(
                f"Multiple URLs ({len(urls)}) may reduce engagement."
            )
        
        # Check for repetitive characters
        if self.has_repetitive_characters(content):
            validation_results['warnings'].append(
                "Contains repetitive characters that may trigger spam filters"
            )
        
        # Check for all caps
        if self.is_all_caps(content):
            validation_results['warnings'].append(
                "Excessive use of ALL CAPS may be seen as shouting"
            )
        
        # Provide suggestions for improvement
        if not hashtags and validation_results['is_valid']:
            validation_results['suggestions'].append(
                "Consider adding 1-2 relevant hashtags for better reach"
            )
        
        if len(content) < 50 and validation_results['is_valid']:
            validation_results['suggestions'].append(
                "Tweet is quite short. Consider adding more context or value."
            )
        
        return validation_results
    
    def is_profane_content(self, content: str) -> Dict[str, any]:
        """
        Check if content contains profanity or blocked words
        
        Args:
            content: Text to check
            
        Returns:
            Dict with results
        """
        content_lower = content.lower()
        found_words = []
        
        for word in self.blocked_words:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(word.lower()) + r'\b'
            if re.search(pattern, content_lower):
                found_words.append(word)
        
        return {
            'has_profane': len(found_words) > 0,
            'found_words': found_words,
            'blocked_word_count': len(found_words)
        }
    
    def extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        hashtags = re.findall(r'#(\w+)', content)
        return hashtags
    
    def extract_mentions(self, content: str) -> List[str]:
        """Extract mentions from content"""
        mentions = re.findall(r'@(\w+)', content)
        return mentions
    
    def extract_urls(self, content: str) -> List[str]:
        """Extract URLs from content"""
        url_pattern = r'https?://\S+|www\.\S+'
        urls = re.findall(url_pattern, content)
        return urls
    
    def has_repetitive_characters(self, content: str, threshold: int = 3) -> bool:
        """Check for repetitive characters (e.g., '!!!!!', '????')"""
        pattern = r'(.)\1{' + str(threshold) + ',}'
        return bool(re.search(pattern, content))
    
    def is_all_caps(self, content: str, ratio_threshold: float = 0.7) -> bool:
        """Check if text is mostly all caps"""
        # Remove hashtags, mentions, and URLs for this check
        text_only = re.sub(r'[@#]\w+|https?://\S+', '', content)
        words = text_only.split()
        
        if not words:
            return False
        
        # Count words that are all caps
        caps_words = sum(1 for word in words if word.isupper() and len(word) > 1)
        
        # If more than threshold% of words are all caps
        return caps_words / len(words) > ratio_threshold
    
    def validate_hashtags(self, hashtags: List[str]) -> Dict[str, any]:
        """
        Validate hashtags for compliance
        
        Args:
            hashtags: List of hashtags to validate
            
        Returns:
            Dict with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'valid_hashtags': []
        }
        
        for hashtag in hashtags:
            # Remove # if present
            tag = hashtag.lstrip('#')
            
            # Check length
            if len(tag) > 100:  # Twitter's limit for hashtags
                results['errors'].append(f"Hashtag too long: #{tag}")
                results['is_valid'] = False
                continue
            
            # Check characters (only alphanumeric and underscores)
            if not re.match(r'^[A-Za-z0-9_]+$', tag):
                results['errors'].append(f"Invalid characters in hashtag: #{tag}")
                results['is_valid'] = False
                continue
            
            # Check if reserved
            if tag.lower() in self.RESERVED_HASHTAGS:
                results['warnings'].append(f"Reserved hashtag: #{tag}")
            
            # Check if too generic
            if len(tag) < 2:
                results['warnings'].append(f"Very short hashtag: #{tag}")
            
            results['valid_hashtags'].append(tag)
        
        return results


class EnvironmentValidator:
    """Validates environment variables and configuration"""
    
    @staticmethod
    def validate_environment() -> Dict[str, any]:
        """
        Validate all required environment variables
        
        Returns:
            Dict with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'missing_vars': [],
            'invalid_vars': []
        }
        
        # Required variables
        required_vars = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_SECRET'
        ]
        
        # Recommended variables
        recommended_vars = ['TWITTER_BEARER_TOKEN']
        
        # Check required variables
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                results['missing_vars'].append(var)
                results['is_valid'] = False
            elif value.startswith('your_') or 'example' in value:
                results['invalid_vars'].append(var)
                results['is_valid'] = False
        
        # Check recommended variables
        for var in recommended_vars:
            if not os.getenv(var):
                results['warnings'].append(f"Recommended variable missing: {var}")
        
        # Check numeric variables
        tweets_per_week = os.getenv('TWEETS_PER_WEEK', '2')
        try:
            tweets = int(tweets_per_week)
            if tweets < 1 or tweets > 50:
                results['errors'].append('TWEETS_PER_WEEK must be between 1 and 50')
                results['is_valid'] = False
        except ValueError:
            results['errors'].append('TWEETS_PER_WEEK must be a number')
            results['is_valid'] = False
        
        # Check timezone
        timezone = os.getenv('TIMEZONE', 'UTC')
        try:
            import pytz
            if timezone not in pytz.all_timezones:
                results['warnings'].append(f"Timezone '{timezone}' may not be valid")
        except ImportError:
            # pytz not available, skip validation
            pass
        
        # Check dry run
        dry_run = os.getenv('DRY_RUN', 'False')
        if dry_run.lower() not in ['true', 'false', 'yes', 'no', '0', '1']:
            results['warnings'].append('DRY_RUN should be True or False')
        
        # Prepare error messages
        if results['missing_vars']:
            results['errors'].append(
                f"Missing required variables: {', '.join(results['missing_vars'])}"
            )
        
        if results['invalid_vars']:
            results['errors'].append(
                f"Variables contain placeholder values: {', '.join(results['invalid_vars'])}"
            )
        
        return results
    
    @staticmethod
    def validate_file_permissions() -> Dict[str, any]:
        """
        Validate file and directory permissions
        
        Returns:
            Dict with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        required_dirs = [
            './storage',
            './storage/logs',
            './src/content/data'
        ]
        
        required_files = [
            './.env',
            './src/content/data/crypto_topics.json',
            './src/content/data/finance_quotes.json',
            './src/content/data/jokes.json',
            './src/content/data/social_topics.json'
        ]
        
        # Check directories
        for directory in required_dirs:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created directory: {directory}")
                except Exception as e:
                    results['errors'].append(f"Cannot create directory {directory}: {str(e)}")
                    results['is_valid'] = False
            elif not os.path.isdir(directory):
                results['errors'].append(f"Path exists but is not a directory: {directory}")
                results['is_valid'] = False
            else:
                # Check write permissions
                test_file = os.path.join(directory, '.write_test')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                except Exception as e:
                    results['warnings'].append(f"No write permission in {directory}: {str(e)}")
        
        # Check files
        for filepath in required_files:
            if not os.path.exists(filepath):
                if filepath == './.env':
                    results['errors'].append(f"Missing required file: {filepath}")
                    results['is_valid'] = False
                else:
                    results['warnings'].append(f"Missing data file: {filepath}")
        
        return results


class ScheduleValidator:
    """Validates schedule configuration"""
    
    @staticmethod
    def validate_schedule(schedule_config: Dict) -> Dict[str, any]:
        """
        Validate schedule configuration
        
        Args:
            schedule_config: Schedule configuration dictionary
            
        Returns:
            Dict with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check required keys
            required_keys = ['frequency', 'count', 'time_range', 'days']
            for key in required_keys:
                if key not in schedule_config:
                    results['errors'].append(f"Missing schedule key: {key}")
                    results['is_valid'] = False
            
            if not results['is_valid']:
                return results
            
            # Validate count
            count = schedule_config.get('count', 0)
            if not isinstance(count, int) or count < 1 or count > 50:
                results['errors'].append('Schedule count must be between 1 and 50')
                results['is_valid'] = False
            
            # Validate frequency
            frequency = schedule_config.get('frequency', '').lower()
            if frequency not in ['hourly', 'daily', 'weekly', 'monthly']:
                results['warnings'].append(f"Unusual frequency: {frequency}")
            
            # Validate time range
            time_range = schedule_config.get('time_range', {})
            if 'start' not in time_range or 'end' not in time_range:
                results['errors'].append('Time range must have start and end')
                results['is_valid'] = False
            else:
                try:
                    if isinstance(time_range['start'], str):
                        # Parse string time
                        start_time = datetime.strptime(time_range['start'], '%H:%M').time()
                    else:
                        start_time = time_range['start']
                    
                    if isinstance(time_range['end'], str):
                        end_time = datetime.strptime(time_range['end'], '%H:%M').time()
                    else:
                        end_time = time_range['end']
                    
                    if start_time >= end_time:
                        results['errors'].append('Start time must be before end time')
                        results['is_valid'] = False
                except Exception as e:
                    results['errors'].append(f"Invalid time format: {str(e)}")
                    results['is_valid'] = False
            
            # Validate days
            days = schedule_config.get('days', [])
            if not isinstance(days, list):
                results['errors'].append('Days must be a list')
                results['is_valid'] = False
            else:
                for day in days:
                    if not isinstance(day, int) or day < 0 or day > 6:
                        results['errors'].append(f"Invalid day value: {day}. Must be 0-6")
                        results['is_valid'] = False
            
            # Check for reasonable distribution
            if len(days) < 2 and count > 1:
                results['warnings'].append('Only one day selected for multiple tweets')
            
        except Exception as e:
            results['errors'].append(f"Schedule validation error: {str(e)}")
            results['is_valid'] = False
        
        return results


class ConfigValidator:
    """Validates application configuration"""
    
    @staticmethod
    def validate_config(config_data: Dict) -> Dict[str, any]:
        """
        Validate application configuration
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            Dict with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate categories
            if 'categories' not in config_data:
                results['errors'].append('Missing categories configuration')
                results['is_valid'] = False
            else:
                categories = config_data['categories']
                total_weight = sum(categories.values())
                
                if abs(total_weight - 1.0) > 0.01:  # Allow small rounding errors
                    results['errors'].append(f'Category weights sum to {total_weight}, should be 1.0')
                    results['is_valid'] = False
                
                # Check for empty categories
                for category, weight in categories.items():
                    if weight <= 0:
                        results['warnings'].append(f'Category {category} has zero or negative weight')
            
            # Validate timezone
            timezone = config_data.get('timezone', 'UTC')
            if not timezone:
                results['warnings'].append('Timezone not specified, using UTC')
            
        except Exception as e:
            results['errors'].append(f"Config validation error: {str(e)}")
            results['is_valid'] = False
        
        return results


# Convenience functions
def validate_tweet_content(content: str, max_length: int = 280) -> Dict[str, any]:
    """Convenience function to validate tweet content"""
    validator = ContentValidator()
    return validator.validate_tweet_content(content, max_length)


def validate_environment() -> Dict[str, any]:
    """Convenience function to validate environment"""
    return EnvironmentValidator.validate_environment()


def validate_schedule(schedule_config: Dict) -> Dict[str, any]:
    """Convenience function to validate schedule"""
    return ScheduleValidator.validate_schedule(schedule_config)


def validate_hashtags(hashtags: List[str]) -> Dict[str, any]:
    """Convenience function to validate hashtags"""
    validator = ContentValidator()
    return validator.validate_hashtags(hashtags)


def is_profane_content(content: str) -> Dict[str, any]:
    """Convenience function to check for profanity"""
    validator = ContentValidator()
    return validator.is_profane_content(content)


# Test function
def run_validations() -> Dict[str, any]:
    """Run all validations and return combined results"""
    logger.info("Running all validations...")
    
    results = {
        'environment': validate_environment(),
        'file_permissions': EnvironmentValidator.validate_file_permissions(),
        'content_validator': ContentValidator(),
        'overall_valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check environment validation
    if not results['environment']['is_valid']:
        results['overall_valid'] = False
        results['errors'].extend(results['environment']['errors'])
    
    results['warnings'].extend(results['environment']['warnings'])
    
    # Check file permissions
    if not results['file_permissions']['is_valid']:
        results['overall_valid'] = False
        results['errors'].extend(results['file_permissions']['errors'])
    
    results['warnings'].extend(results['file_permissions']['warnings'])
    
    # Log results
    if results['overall_valid']:
        logger.info("✅ All validations passed")
    else:
        logger.error("❌ Validations failed")
        for error in results['errors']:
            logger.error(f"  - {error}")
    
    if results['warnings']:
        logger.warning("⚠️  Validation warnings:")
        for warning in results['warnings']:
            logger.warning(f"  - {warning}")
    
    return results
