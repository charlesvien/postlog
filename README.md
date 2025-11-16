# Postlog

Python application that sends a stream of test log data to PostHog using OTLP over HTTP.

## Prerequisites

- Python 3.7+
- PostHog instance with OTLP endpoint

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your PostHog API key:
```
POSTHOG_API_KEY=your_api_key_here
```

## Usage

Run the application:
```bash
python main.py
```

The script will continuously send log messages every second.

By default, logs are sent to `http://localhost:4318/v1/logs`. You can modify the endpoint in `main.py` if needed.