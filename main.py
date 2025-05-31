from app.optisign_bot import OptiSignBot
from dotenv import load_dotenv
import os
import sys

def main():
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Initialize the bot
    bot = OptiSignBot(openai_api_key=api_key, max_articles=50)
    
    # bot.delete_all_files()
    # Scrape articles
    print("Scraping articles...")
    total_articles = bot.scrape_articles()
    print(f"Scraped {total_articles} articles")
    
    

if __name__ == "__main__":
    main()
