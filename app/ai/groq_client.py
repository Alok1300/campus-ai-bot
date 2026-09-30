from groq import Groq
from app.config import settings

def get_groq_client():
    return Groq(api_key=settings.GROQ_API_KEY)
