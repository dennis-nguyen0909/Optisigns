from app.optisign_bot import OptiSignBot
from dotenv import load_dotenv
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('optisign_bot.log')
    ]
)
logger = logging.getLogger(__name__)

def run_chat():
    """Run the bot in interactive chat mode"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize the bot
        bot = OptiSignBot(openai_api_key=api_key, max_articles=40)
        
        # Set up OpenAI assistant
        logger.info("Setting up OpenAI assistant...")
        bot.setup_openai_assistant()
        
        # Interactive question loop
        logger.info("\nOptiBot is ready! Type 'quit' to exit.")
        while True:
            try:
                # Flush stdout to ensure prompt is visible
                sys.stdout.flush()
                question = input("\nEnter your question: ").strip()
                
                if not question:
                    continue
                    
                if question.lower() == 'quit':
                    break
                    
                logger.info("Getting response...")
                response = bot.ask_question(question)
                print(f"\nResponse: {response}")
                
            except EOFError:
                logger.error("No input available. Please run the container with -it flags:")
                print("docker run -it -e OPENAI_API_KEY=your_key optisignbot")
                break
            except KeyboardInterrupt:
                logger.info("Goodbye!")
                break
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                break
                
    except Exception as e:
        logger.error(f"Error in chat mode: {str(e)}")
        raise

if __name__ == "__main__":
    run_chat() 