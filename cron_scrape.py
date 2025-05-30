import logging
import sys
import os
from datetime import datetime

# Import from the app directory
from app.optisign_bot import OptiSignBot
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/cron_scrape.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_scrape():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize the bot
        bot = OptiSignBot(openai_api_key=api_key, max_articles=50)
        
        # Scrape articles
        logger.info(f"Starting article scraping at {datetime.now().isoformat()}")
        total_articles = bot.scrape_articles()
        logger.info(f"Scraping completed. Total articles processed: {total_articles}")
        
        # Set up OpenAI assistant
        logger.info("Setting up OpenAI assistant...")
        bot.setup_openai_assistant()
        logger.info("OpenAI assistant setup completed")
        
        # Log completion
        logger.info(f"Job completed successfully at {datetime.now().isoformat()}")
        
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        # Don't raise the exception to prevent job failure
        sys.exit(1)

if __name__ == "__main__":
    run_scrape() 