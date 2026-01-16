import os
import sys
import argparse
from pathlib import Path

# Add the project root to Python path
# This allows imports like "from src.main import AutoTweetBot"
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if all required environment and files exist"""
    print("🔍 Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        return False
    
    # Check if .env exists
    env_file = project_root / '.env'
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        print("   Then edit .env with your Twitter API keys")
        return False
    
    # Check for required directories
    required_dirs = [
        'storage',
        'storage/logs',
        'src/content/data'
    ]
    
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            print(f"⚠️  Directory missing: {dir_path}")
            (project_root / dir_path).mkdir(parents=True, exist_ok=True)
            print(f"   Created: {dir_path}")
    
    # Check for data files
    data_files = [
        'src/content/data/crypto_topics.json',
        'src/content/data/finance_quotes.json',
        'src/content/data/jokes.json',
        'src/content/data/social_topics.json'
    ]
    
    missing_files = []
    for file_path in data_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️  Missing data files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n   Creating sample data files...")
        create_sample_data()
    
    print("✅ Environment check passed")
    return True

def create_sample_data():
    """Create sample data files if they don't exist"""
    import json
    
    # Sample crypto data
    crypto_data = {
        "topics": ["Bitcoin", "Ethereum", "DeFi", "NFTs", "Web3"],
        "templates": ["Thoughts on {topic} in 2026? 🤔 #Crypto"],
        "hashtags": ["#Crypto", "#Bitcoin", "#Ethereum"]
    }
    
    # Sample finance data
    finance_data = {
        "quotes": [
            {"text": "The stock market is a device for transferring money from the impatient to the patient.", "author": "Warren Buffett"}
        ],
        "tips": ["Start investing early. Even small amounts can grow significantly over time."],
        "statistics": ["If you invest $100 a month at 8% return for 40 years, you'll have over $310,000."]
    }
    
    # Sample jokes data
    jokes_data = {
        "programming": ["Why do programmers prefer dark mode? Because light attracts bugs! 🐛"],
        "crypto": ["What's a cryptocurrency's favorite type of music? Block & roll!"]
    }
    
    # Sample social data
    social_data = {
        "topics": ["The impact of social media on mental health"],
        "questions": ["How has social media changed the way we form relationships?"],
        "insights": ["Humans have a fundamental need for social connection, which technology can facilitate but not fully replace."]
    }
    
    data_to_create = {
        'src/content/data/crypto_topics.json': crypto_data,
        'src/content/data/finance_quotes.json': finance_data,
        'src/content/data/jokes.json': jokes_data,
        'src/content/data/social_topics.json': social_data
    }
    
    for file_path, data in data_to_create.items():
        full_path = project_root / file_path
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"   Created: {file_path}")

def show_banner():
    """Display ASCII art banner"""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║      🐦 AUTO TWEET BOT FOR X.COM 🚀       ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)

def show_disclaimer():
    """Show disclaimer on first run"""
    disclaimer_shown = project_root / '.disclaimer_shown'
    
    if not disclaimer_shown.exists():
        print("\n" + "="*60)
        print("⚠️   IMPORTANT DISCLAIMER & WARNING   ⚠️")
        print("="*60)
        print("""
This software is for EDUCATIONAL PURPOSES ONLY.

By using this bot, you acknowledge and agree that:

1. You are solely responsible for Twitter/X compliance
2. Automation may result in account suspension or ban
3. No warranty or guarantee is provided
4. Use at your own risk
5. Review DISCLAIMER.txt for full terms

Full documentation in: legal/ directory
        """)
        print("="*60)
        
        response = input("\nDo you understand and accept these terms? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("You must accept the terms to use this software.")
            sys.exit(1)
        
        # Mark disclaimer as shown
        disclaimer_shown.touch()
        print("\n✅ Disclaimer accepted. Continuing...\n")

def setup_logging():
    """Setup logging configuration"""
    from src.core.logger import setup_logger
    return setup_logger('run')

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Auto Tweet Bot for X.com - Post tweets automatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start the bot normally
  %(prog)s --once             # Post a single test tweet
  %(prog)s --dry-run          # Test without posting
  %(prog)s --list-scheduled   # Show scheduled tweets
  %(prog)s --validate         # Run validation checks
  %(prog)s --stats            # Show statistics
        """
    )
    
    parser.add_argument('--once', action='store_true',
                       help='Post a single tweet and exit')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test without actually posting to Twitter')
    parser.add_argument('--list-scheduled', action='store_true',
                       help='List scheduled tweets and exit')
    parser.add_argument('--validate', action='store_true',
                       help='Run validation checks and exit')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics from history')
    parser.add_argument('--export', type=str, metavar='FORMAT',
                       choices=['json', 'csv'],
                       help='Export tweet history (json or csv)')
    parser.add_argument('--version', action='store_true',
                       help='Show version information')
    parser.add_argument('--setup', action='store_true',
                       help='Run setup wizard for first-time configuration')
    
    args = parser.parse_args()
    
    # Show banner
    show_banner()
    
    # Show disclaimer on first run
    show_disclaimer()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Setup logging
    logger = setup_logging()
    
    # Handle version request
    if args.version:
        from src import __version__
        print(f"Auto Tweet Bot Version: {__version__}")
        sys.exit(0)
    
    # Handle setup wizard
    if args.setup:
        run_setup_wizard()
        sys.exit(0)
    
    # Handle validation request
    if args.validate:
        run_validations()
        sys.exit(0)
    
    # Handle export request
    if args.export:
        export_history(args.export)
        sys.exit(0)
    
    # Handle stats request
    if args.stats:
        show_statistics()
        sys.exit(0)
    
    # Set environment variable for dry run
    if args.dry_run:
        os.environ['DRY_RUN'] = 'True'
        logger.info("DRY RUN mode enabled - no tweets will be posted")
    
    # Import main bot class (after environment checks)
    from src.main import AutoTweetBot
    
    # Create bot instance
    bot = AutoTweetBot()
    
    try:
        if args.once:
            logger.info("Running single tweet mode...")
            bot.run_once()
        elif args.list_scheduled:
            # We need to initialize scheduler but not start it
            from src.core.scheduler import TweetScheduler
            scheduler = TweetScheduler()
            scheduler.schedule_tweets()
            jobs = scheduler.get_scheduled_jobs()
            
            print("\n📅 Scheduled Tweets:")
            print("="*60)
            for job in jobs:
                print(f"• {job['name']}")
                print(f"  Next Run: {job['next_run']}")
                print(f"  Trigger: {job['trigger']}")
                print()
        else:
            # Start the bot normally
            logger.info("Starting Auto Tweet Bot...")
            bot.start()
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        bot.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)

def run_setup_wizard():
    """Interactive setup wizard for first-time users"""
    print("\n" + "="*60)
    print("🛠️  SETUP WIZARD - First Time Configuration")
    print("="*60)
    
    # Check if .env exists
    env_file = project_root / '.env'
    if env_file.exists():
        print("\n✅ .env file already exists")
        edit = input("Do you want to edit it? (yes/no): ")
        if edit.lower() in ['yes', 'y']:
            edit_env_file()
    else:
        print("\n❌ .env file not found")
        create = input("Create from template? (yes/no): ")
        if create.lower() in ['yes', 'y']:
            create_env_file()
    
    # Check data files
    print("\n📁 Checking data files...")
    create_sample_data()
    
    # Test Twitter connection
    print("\n🔗 Testing Twitter API connection...")
    test_twitter_connection()
    
    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python run.py --once (to test)")
    print("2. Run: python run.py (to start the bot)")
    print("="*60)

def create_env_file():
    """Create .env file from template"""
    env_example = project_root / '.env.example'
    env_file = project_root / '.env'
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return
    
    # Read template
    with open(env_example, 'r') as f:
        template = f.read()
    
    # Get user input
    print("\nPlease enter your Twitter API credentials:")
    print("(Get these from https://developer.twitter.com)")
    print()
    
    api_key = input("Twitter API Key: ").strip()
    api_secret = input("Twitter API Secret: ").strip()
    access_token = input("Access Token: ").strip()
    access_secret = input("Access Token Secret: ").strip()
    
    # Replace placeholders
    template = template.replace('your_api_key_here', api_key)
    template = template.replace('your_api_secret_here', api_secret)
    template = template.replace('your_access_token_here', access_token)
    template = template.replace('your_access_secret_here', access_secret)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(template)
    
    print(f"\n✅ .env file created at: {env_file}")
    print("⚠️  IMPORTANT: Keep this file secure and never share it!")

def edit_env_file():
    """Edit existing .env file"""
    env_file = project_root / '.env'
    
    # Simple editor
    import subprocess
    import platform
    
    if platform.system() == 'Windows':
        subprocess.call(['notepad', str(env_file)])
    elif platform.system() == 'Darwin':  # macOS
        subprocess.call(['open', '-t', str(env_file)])
    else:  # Linux/Unix
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.call([editor, str(env_file)])
    
    print(f"\n✅ .env file edited")

def test_twitter_connection():
    """Test Twitter API connection"""
    try:
        from src.core.twitter_client import TwitterClient
        client = TwitterClient()
        
        user_info = client.get_user_info()
        if user_info:
            print(f"✅ Connected to Twitter as: @{user_info['username']}")
            print(f"   Name: {user_info['name']}")
            print(f"   ID: {user_info['id']}")
        else:
            print("❌ Failed to get user info")
            
    except Exception as e:
        print(f"❌ Twitter connection failed: {str(e)}")
        print("   Please check your API credentials in .env")

def run_validations():
    """Run all validation checks"""
    print("\n" + "="*60)
    print("✅ VALIDATION CHECKS")
    print("="*60)
    
    from src.utils.validators import run_validations as run_val
    results = run_val()
    
    if results['overall_valid']:
        print("\n🎉 All validations passed!")
    else:
        print("\n❌ Validation failed. Please fix the issues above.")
        sys.exit(1)

def export_history(format='json'):
    """Export tweet history"""
    from src.utils.history_manager import HistoryManager
    
    print(f"\nExporting tweet history as {format.upper()}...")
    manager = HistoryManager()
    
    timestamp = os.path.expanduser(f"~/tweets_export_{os.path.basename(project_root)}_{os.path.getpid()}.{format}")
    success = manager.export_history(format, timestamp)
    
    if success:
        print(f"✅ History exported to: {timestamp}")
    else:
        print("❌ Export failed")
        sys.exit(1)

def show_statistics():
    """Show statistics from tweet history"""
    from src.utils.history_manager import HistoryManager
    from datetime import datetime, timedelta
    
    print("\n" + "="*60)
    print("📊 TWEET STATISTICS")
    print("="*60)
    
    manager = HistoryManager()
    stats = manager.get_statistics()
    
    if not stats:
        print("No tweet history found")
        return
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Tweets: {stats['total_tweets']}")
    print(f"   Successful: {stats['successful_tweets']}")
    print(f"   Failed: {stats['failed_tweets']}")
    print(f"   Success Rate: {stats['success_rate']:.1%}")
    print(f"   Total Impressions: {stats['total_impressions']:,}")
    print(f"   Total Engagements: {stats['total_engagements']:,}")
    
    if stats['total_impressions'] > 0:
        print(f"   Engagement Rate: {stats['engagement_rate']:.2%}")
    
    print(f"\n🎯 Category Distribution:")
    for category, count in stats['categories'].items():
        percentage = (count / stats['total_tweets']) * 100
        print(f"   {category.capitalize():12} {count:3d} tweets ({percentage:.1f}%)")
    
    # Recent tweets
    recent = manager.get_recent_tweets(5)
    if recent:
        print(f"\n📝 Recent Tweets (last 5):")
        for i, tweet in enumerate(recent, 1):
            date = datetime.fromisoformat(tweet['timestamp'].replace('Z', '+00:00'))
            print(f"   {i}. [{date.strftime('%Y-%m-%d')}] {tweet['content'][:60]}...")

if __name__ == '__main__':
    main()
