import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    GROQ_API_KEY: str
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    WALKING_SPEED_KMH: float = 5.0
    CONFIDENCE_THRESHOLD: float = 0.8

settings = Settings()
