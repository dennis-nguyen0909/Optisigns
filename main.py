from optisign_bot import OptiSignBot
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
    bot = OptiSignBot(openai_api_key=api_key, max_articles=40)
    
    # Scrape articles
    print("Scraping articles...")
    total_articles = bot.scrape_articles()
    print(f"Scraped {total_articles} articles")
    
    # Set up OpenAI assistant
    print("Setting up OpenAI assistant...")
    bot.setup_openai_assistant()
    
    # Interactive question loop
    print("\nOptiBot is ready! Type 'quit' to exit.")
    while True:
        try:
            # Flush stdout to ensure prompt is visible
            sys.stdout.flush()
            question = input("\nEnter your question: ").strip()
            
            if not question:
                continue
                
            if question.lower() == 'quit':
                break
                
            print("\nGetting response...")
            response = bot.ask_question(question)
            print(f"\nResponse: {response}")
            
        except EOFError:
            print("\nError: No input available. Please run the container with -it flags:")
            print("docker run -it -e OPENAI_API_KEY=your_key optisignbot")
            break
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            break

if __name__ == "__main__":
    main()
