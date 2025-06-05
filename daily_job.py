import logging
import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

from app.optisign_bot import OptiSignBot

# Set up logging for DigitalOcean
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_daily_job():
    """Single execution of OptisignBot for DigitalOcean App Platform"""
    try:
        logger.info(f"Starting OptisignBot daily job at {datetime.now().isoformat()}")
        
        # Load environment variables
        load_dotenv()
        
        # Get OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            sys.exit(1)
        
        # Initialize the bot
        bot = OptiSignBot(openai_api_key=api_key, max_articles=40)
        
        # Scrape articles
        logger.info("Starting article scraping...")
        total_articles = bot.scrape_articles()
        logger.info(f"Scraping completed. Total articles processed: {total_articles}")
        
        # Setup OpenAI assistant
        logger.info("Setting up OpenAI assistant...")
        bot.setup_openai_assistant()
        logger.info("OpenAI assistant setup completed")
        
        logger.info(f"Daily job completed successfully at {datetime.now().isoformat()}")
        
        # For DigitalOcean App Platform, we sleep for 24 hours then exit
        # The platform will restart the worker automatically
        logger.info("Waiting 24 hours for next execution...")
        time.sleep(24 * 60 * 60)  # Sleep for 24 hours
        
    except Exception as e:
        logger.error(f"Error during daily job execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_daily_job() 