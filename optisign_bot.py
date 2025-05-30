import requests
import html2text
import os
import glob
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

class OptiSignBot:
    def __init__(self, openai_api_key: str, max_articles: int = 40):
        self.max_articles = max_articles
        self.url_section = "https://support.optisigns.com/api/v2/help_center/en-us/sections"
        self.url_article = "https://support.optisigns.com/api/v2/help_center/en-us/sections/{section_id}/articles"
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant = None
        self.vector_store = None
        
        # Create articles directory if it doesn't exist
        if not os.path.exists("articles"):
            os.makedirs("articles")

    def fetch_all_sections(self) -> Dict:
        response = requests.get(self.url_section)
        if response.status_code != 200:
            raise Exception(f"Error fetching sections: {response.status_code}")
        return response.json()

    def get_all_section_ids(self) -> List[int]:
        sections = self.fetch_all_sections()
        sectionIds = []
        for item in sections['sections']:
            sectionIds.append(item['id'])
        return sectionIds

    def fetch_articles_from_section(self, section_id: int) -> List[Dict]:
        url = self.url_article.format(section_id=section_id)
        params = {
            "sort_by": "position",
            "sort_order": "desc",
            "per_page": 100
        }

        articles = []
        while url:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                raise Exception(f"Error fetching articles: {response.status_code}")
            data = response.json()
            articles.extend(data.get("articles", []))
            url = data.get("next_page")

        return articles

    def save_as_markdown(self, article: Dict) -> None:
        """Save an article as markdown file"""
        slug = article["title"].lower().replace(" ", "-").replace("/", "-")
        markdown = html2text.html2text(article["body"])
        with open(f"articles/{slug}.md", "w", encoding="utf-8") as f:
            f.write(f"# {article['title']}\n\n")
            f.write(markdown)

    def delete_all_files(self) -> None:
        """Delete all files in the articles directory"""
        for file in os.listdir("articles"):
            os.remove(f"articles/{file}")

    def scrape_articles(self) -> int:
        self.delete_all_files()
        section_ids = self.get_all_section_ids()
        
        total_articles = 0
        for section_id in section_ids:
            if total_articles >= self.max_articles:
                break
                
            all_articles = self.fetch_articles_from_section(section_id)
            for article in all_articles:
                if total_articles >= self.max_articles:
                    break
                self.save_as_markdown(article)
                total_articles += 1
                
        return total_articles

    def setup_openai_assistant(self) -> None:
        self.assistant = self.client.beta.assistants.create(
            name="OptiBot",
            instructions="You are OptiBot, the customer-support bot for OptiSigns.com. Tone: helpful, factual, concise. Only answer using the uploaded docs. Max 5 bullet points; else link to the doc. Cite up to 3 'Article URL:' lines per reply.",
            model="gpt-4-turbo-preview",
            tools=[{"type": "file_search"}],
        )

        self.vector_store = self.client.vector_stores.create(name="OptiSigns")

        file_paths = glob.glob("articles/*.md")
        file_streams = [open(path, "rb") for path in file_paths]

        file_batch = self.client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store.id,
            files=file_streams
        )

        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [self.vector_store.id]}}
        )

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