from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"  # default if not in .env
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"  # default if not in .env
    EMAIL_SENDER: str
    EMAIL_PASSWORD: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 500
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str
    ALGORITHM: str
    RAZORPAY_KEY: str = ""  
    RAZORPAY_SECRET: str = ""  
    STRIPE_CURRENCY: str = "usd"


    class Config:
        env_file = ".env"


settings = Settings()

# BaseSettings reads .env and populates the fields in Settings class. now we can import settings from this module and access settings.DATABASE_URL to get the database connection string.