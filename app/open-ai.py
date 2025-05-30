from openai import OpenAI
import os
from dotenv import load_dotenv
import glob
from pathlib import Path

# Get the absolute path to the .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please check if .env file exists and contains the API key.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# STEP 1: Create an assistant
assistant = client.beta.assistants.create(
  name="OptiBot",
  instructions="You are OptiBot, the customer-support bot for OptiSigns.com. Tone: helpful, factual, concise. Only answer using the uploaded docs. Max 5 bullet points; else link to the doc. Cite up to 3 'Article URL:' lines per reply.",
  model="gpt-4-turbo-preview",
  tools=[{"type": "file_search"}],
)

# STEP 2: Create a vector store 
vector_store = client.vector_stores.create(name="OptiSigns")

file_paths = glob.glob("articles/*.md")
file_streams = [open(path, "rb") for path in file_paths]

file_batch = client.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

# STEP 3: Update the assistant to use the vector store
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)

# Create a thread with a question about OptiSigns
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "What Happens if Your Screen Already",
    }
  ]
)

# STEP 4: Run the assistant
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# STEP 4: Get response from Assistant
messages = client.beta.threads.messages.list(thread_id=thread.id)

for message in reversed(messages.data):
    if message.role == "assistant":
        print("Assistant reply:")
        print(message.content[0].text.value)
