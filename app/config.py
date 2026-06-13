"""Application configuration via environment variables."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Sarvam AI
    sarvam_api_key: str = ""
    sarvam_base_url: str = "https://api.sarvam.ai"

    # WhatsApp Cloud API
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    webhook_verify_token: str = "jankalyan_verify_2024"

    # Database
    database_path: str = "schemes.db"

    # App
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}



settings = Settings()
