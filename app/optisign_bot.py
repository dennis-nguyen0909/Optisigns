import requests
import html2text
import os
import glob
import json
import hashlib
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

class OptiSignBot:
    def __init__(self, openai_api_key: str, max_articles: int = 40):
        self.max_articles = max_articles
        self.url_section = "https://support.optisigns.com/api/v2/help_center/en-us/sections"
        self.url_article = "https://support.optisigns.com/api/v2/help_center/en-us/sections/{section_id}/articles"
        self.metadata_file = "articles/metadata.json"
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant = None
        self.vector_store = None
        
        # Create articles directory if it doesn't exist
        if not os.path.exists("articles"):
            os.makedirs("articles")

    def load_metadata(self) -> Dict:
        """Load article metadata from file"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def save_metadata(self, metadata: Dict) -> None:
        """Save article metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def calculate_article_hash(self, article: Dict) -> str:
        """Calculate hash of article content"""
        content = f"{article['title']}{article['body']}"
        return hashlib.md5(content.encode()).hexdigest()

    def fetch_all_sections(self) -> Dict:
        try:
            response = requests.get(self.url_section, timeout=30)
            if response.status_code != 200:
                raise Exception(f"Error fetching sections: {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"Error fetching sections: {e}")
            raise

    def get_all_section_ids(self) -> List[int]:
        sections = self.fetch_all_sections()
        sectionIds = []
        for item in sections['sections']:
            sectionIds.append(item['id'])
        return sectionIds

    def fetch_articles_from_section(self, section_id: int) -> List[Dict]:
        try:
            url = self.url_article.format(section_id=section_id)
            params = {
                "sort_by": "position",
                "sort_order": "desc",
                "per_page": 100
            }

            articles = []
            while url:
                response = requests.get(url, params=params, timeout=30)
                if response.status_code != 200:
                    raise Exception(f"Error fetching articles: {response.status_code}")
                data = response.json()
                articles.extend(data.get("articles", []))
                url = data.get("next_page")
                params = None

            return articles
        except Exception as e:
            print(f"Error fetching articles from section {section_id}: {e}")
            raise

    def save_as_markdown(self, article: Dict) -> None:
        """Save an article as markdown file"""
        try:
            slug = article["title"].lower().replace(" ", "-").replace("/", "-")
            slug = "".join(c for c in slug if c.isalnum() or c in ('-', '_')).rstrip()
            
            markdown = html2text.html2text(article["body"])
            with open(f"articles/{slug}.md", "w", encoding="utf-8") as f:
                f.write(f"# {article['title']}\n\n")
                f.write(markdown)
        except Exception as e:
            print(f"Error saving article: {e}")

    def delete_all_files(self) -> None:
        try:
            for file in os.listdir("articles"):
                os.remove(f"articles/{file}")
        except Exception as e:
            print(f"Error deleting files: {e}")

    def scrape_articles(self) -> int:
        """Scrape articles with delta updates"""
        try:
            # Load existing metadata
            metadata = self.load_metadata()
            section_ids = self.get_all_section_ids()
            
            total_articles = 0
            updated_articles = 0
            new_articles = 0
            
            for section_id in section_ids:
                if total_articles >= self.max_articles:
                    break
                    
                try:
                    all_articles = self.fetch_articles_from_section(section_id)
                    for article in all_articles:
                        if total_articles >= self.max_articles:
                            break
                            
                        article_id = str(article['id'])
                        current_hash = self.calculate_article_hash(article)
                        last_modified = article.get('updated_at', article.get('created_at'))
                        
                        # Check if article needs update
                        needs_update = False
                        if article_id not in metadata:
                            needs_update = True
                            new_articles += 1
                        elif (metadata[article_id]['hash'] != current_hash or 
                              metadata[article_id]['last_modified'] != last_modified):
                            needs_update = True
                            updated_articles += 1
                        
                        if needs_update:
                            self.save_as_markdown(article)
                            metadata[article_id] = {
                                'hash': current_hash,
                                'last_modified': last_modified,
                                'title': article['title'],
                                'slug': article["title"].lower().replace(" ", "-").replace("/", "-")
                            }
                        
                        total_articles += 1
                except Exception as e:
                    print(f"Error processing section {section_id}: {e}")
                    continue
            
            # Save updated metadata
            self.save_metadata(metadata)
            
            print(f"Total articles processed: {total_articles}")
            print(f"New articles: {new_articles}")
            print(f"Updated articles: {updated_articles}")
            
            return total_articles
        except Exception as e:
            print(f"Error during scraping: {e}")
            raise

    def setup_openai_assistant(self) -> None:
        """Set up OpenAI assistant with vector store"""
        # Create unique name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        assistant_name = f"OptiBot_v{timestamp}"
        vector_store_name = f"OptiSigns_v{timestamp}"
        
        print(f"Creating assistant: {assistant_name}")
        
        self.assistant = self.client.beta.assistants.create(
            name=assistant_name,
            instructions="You are OptiBot, the customer-support bot for OptiSigns.com. Tone: helpful, factual, concise. Only answer using the uploaded docs. Max 5 bullet points; else link to the doc. Cite up to 3 'Article URL:' lines per reply.",
            model="gpt-4-turbo-preview",
            tools=[{"type": "file_search"}],
        )

        # Create new vector store
        self.vector_store = self.client.vector_stores.create(name=vector_store_name)

        # Get all markdown files
        file_paths = glob.glob("articles/*.md")
        file_streams = [open(path, "rb") for path in file_paths]

        # Upload files to vector store
        file_batch = self.client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store.id,
            files=file_streams
        )

        # Update assistant with vector store
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [self.vector_store.id]}}
        )
        
        print(f"Assistant created successfully with ID: {self.assistant.id}")

    def ask_question(self, question: str) -> str:
        if not self.assistant:
            raise Exception("Assistant not set up. Call setup_openai_assistant() first.")

        # Create a thread with the question
        thread = self.client.beta.threads.create(
            messages=[{"role": "user", "content": question}]
        )

        # Run the assistant
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=self.assistant.id
        )

        # Get the response
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        
        for message in reversed(messages.data):
            if message.role == "assistant":
                return message.content[0].text.value
                
        return "No response received from assistant." 