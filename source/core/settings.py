import os
from typing import Union
from pydantic import model_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_TITLE: str = "MAX - Ultimate Sports Betting AI"
    VERSION: str = "2.0.0"
    APP_ENV: str = os.environ.get("APP_ENV", "development")
    DEBUG: bool = os.environ.get("DEBUG", "true").lower() == "true"
    
    # Production settings
    PRODUCTION_URL: str = "https://max-betting-ai.onrender.com"
    PRODUCTION_WS_URL: str = "wss://max-betting-ai.onrender.com"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "realwin_max_secure_jwt_secret_key_2024")
    ALGORITHM: str = "HS256"

    EMAIL_FROM: str = os.environ.get("EMAIL_FROM", "noreply@realwin.ai")
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "https://realwin-frontend-master.vercel.app")

    AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")

    POSTGRES_USER: str = os.environ.get("DB_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("DB_PASSWORD", "postgres")
    POSTGRES_DB: str = os.environ.get("DB_NAME", "postgres")
    POSTGRES_HOST: str = os.environ.get("DB_HOST", "localhost")
    POSTGRES_PORT: int = int(os.environ.get("DB_PORT", "5432"))
    POSTGRES_URI: str = ""  # Will be set in validator

    POSTGRES_TEST_URI: str = ""  # Will be set in validator
    BASE_URL_LOCAL: str = os.environ.get("BASE_URL_LOCAL", "http://localhost:8000")

    # M.A.X. Webhook System Configuration
    MAX_API_BASE: str = os.environ.get("MAX_API_BASE", "http://localhost:8000")
    WEBHOOK_URL: Union[str, None] = os.environ.get("WEBHOOK_URL", None)
    TELEGRAM_BOT_TOKEN: Union[str, None] = os.environ.get("TELEGRAM_BOT_TOKEN", None)
    WHATSAPP_ACCESS_TOKEN: Union[str, None] = os.environ.get("WHATSAPP_ACCESS_TOKEN", None)
    WHATSAPP_PHONE_NUMBER_ID: Union[str, None] = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", None)
    WHATSAPP_VERIFY_TOKEN: str = os.environ.get(
        "WHATSAPP_VERIFY_TOKEN", "realwin_max_verify"
    )

    # Secondary Timescale/Postgres
    SECOND_DB_USER: Union[str, None] = os.environ.get("SECOND_DB_USER", None)
    SECOND_DB_PASSWORD: Union[str, None] = os.environ.get("SECOND_DB_PASSWORD", None)
    SECOND_DB_HOST: Union[str, None] = os.environ.get("SECOND_DB_HOST", None)
    SECOND_DB_PORT: int = int(os.environ.get("SECOND_DB_PORT", 38009))
    SECOND_DB_NAME: Union[str, None] = os.environ.get("SECOND_DB_NAME", None)

    # Stripe payment settings
    STRIPE_SECRET_KEY: Union[str, None] = os.environ.get("STRIPE_SECRET_KEY", None)
    STRIPE_WEBHOOK_SECRET: Union[str, None] = os.environ.get("STRIPE_WEBHOOK_SECRET", None)
    STRIPE_PRICE_MONTHLY_GBP: Union[str, None] = os.environ.get("STRIPE_PRICE_MONTHLY_GBP", None)
    STRIPE_PRICE_ONE_TIME_1_GBP: Union[str, None] = os.environ.get("STRIPE_PRICE_ONE_TIME_1_GBP", None)
    STRIPE_SUCCESS_URL: str = os.environ.get("STRIPE_SUCCESS_URL", "https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app/payment-success")
    STRIPE_CANCEL_URL: str = os.environ.get("STRIPE_CANCEL_URL", "https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app/subscribe-cancel")
    @model_validator(mode="after")
    def validator(cls, values: "Settings") -> "Settings":
        values.POSTGRES_URI = (
            f"{values.POSTGRES_USER}:{values.POSTGRES_PASSWORD}@"
            f"{values.POSTGRES_HOST}:{values.POSTGRES_PORT}/{values.POSTGRES_DB}"
        )
        return values


def get_settings():
    return Settings()


settings = get_settings()
