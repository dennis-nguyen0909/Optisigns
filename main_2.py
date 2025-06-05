import schedule
import time as tm
import logging
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

from app.optisign_bot import OptiSignBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_daily_optisign_bot():
    """Daily job to scrape articles and setup OpenAI assistant"""
    try:
        logger.info(f"Starting daily OptisignBot at {datetime.now().isoformat()}")
        
        # Load environment variables
        load_dotenv()
        
        # Get OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            return
        
        # Initialize the bot
        bot = OptiSignBot(openai_api_key=api_key, max_articles=40)
        
        # Optional: Clean up old data (uncomment if you want fresh data daily)
        # bot.delete_all_files()
        # metadata_file = "articles/metadata.json"
        # if os.path.exists(metadata_file):
        #     os.remove(metadata_file)
        
        # Scrape articles
        logger.info("Starting article scraping...")
        total_articles = bot.scrape_articles()
        logger.info(f"Scraping completed. Total articles processed: {total_articles}")
        
        # Setup OpenAI assistant
        logger.info("Setting up OpenAI assistant...")
        bot.setup_openai_assistant()
        logger.info("OpenAI assistant setup completed")
        
        logger.info(f"Daily OptisignBot job completed successfully at {datetime.now().isoformat()}")
        
    except Exception as e:
        logger.error(f"Error during daily OptisignBot execution: {str(e)}")

# Schedule the job to run daily at 9:00 AM
schedule.every().day.at("09:00").do(run_daily_optisign_bot)

# You can also schedule multiple times per day if needed:
# schedule.every().day.at("09:00").do(run_daily_optisign_bot)
# schedule.every().day.at("18:00").do(run_daily_optisign_bot)

# Or schedule based on different intervals:
# schedule.every().monday.at("09:00").do(run_daily_optisign_bot)  # Weekly on Monday
# schedule.every(6).hours.do(run_daily_optisign_bot)  # Every 6 hours

def main():
    logger.info("OptisignBot Daily Scheduler started")
    logger.info("Scheduled to run daily at 09:00 AM")
    
    # Run once immediately for testing (comment out in production)
    logger.info("Running initial execution for testing...")
    run_daily_optisign_bot()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        tm.sleep(60)  # Check every minute instead of every second

if __name__ == "__main__":
    main()