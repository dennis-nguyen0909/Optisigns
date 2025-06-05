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
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Initialize the bot
    bot = OptiSignBot(openai_api_key=api_key, max_articles=40)
    
    bot.delete_all_files()
    # Also delete metadata to force re-scrape
    metadata_file = "articles/metadata.json"
    if os.path.exists(metadata_file):
        os.remove(metadata_file)
    
    # Scrape articles
    print("Scraping articles...")
    total_articles = bot.scrape_articles()
    print(f"Scraped {total_articles} articles")
    bot.setup_openai_assistant()
    print("Assistant setup completed!")
    

if __name__ == "__main__":
    main()
