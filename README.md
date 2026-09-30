# Chandigarh University AI Campus Navigation

This is an AI-powered indoor/outdoor campus navigation engine for Chandigarh University.

## Architecture

- **Backend**: Python / FastAPI
- **AI**: Groq API
- **Navigation**: A* pathfinding
- **Data**: JSON based graph structures (ready for PostGIS migration)

## Setup

1. Make sure you have python installed (we use `uv` or standard virtual environment).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Add your GROQ API KEY to `.env`.

## Running the Application

```bash
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest
```
