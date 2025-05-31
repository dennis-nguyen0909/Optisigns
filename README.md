# OptiSignBot

AI-powered customer support chatbot for OptiSigns.com that scrapes help center articles and provides intelligent responses using OpenAI's Assistant API.

## Setup

**Prerequisites**: Python 3.9+, Docker, OpenAI API key

**Environment Variables**: Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Dependencies**:
```bash
pip install -r requirements.txt
```

## How to Run Locally

### Option 1: Python
```bash
git clone https://github.com/dennis-nguyen0909/Optisigns.git
cd OptisignBot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Option 2: Docker
```bash
docker build -t optisignbot .
docker run -e OPENAI_API_KEY=your_key optisignbot
```

**Note**: Container runs once and exits with code 0 (batch job).

### Option 3: Scheduled Worker
```bash
python worker_cron.py  # Daily scraping at midnight UTC
```


