from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://hostel_admin:hostel_pass_123@db:5432/hostel_allocation"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET: str = "change_this_super_secret_key_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Payments are currently SIMULATED (no real gateway wired up). Flip this to False and plug in
    # Razorpay (or any other gateway) in app/api/routes/payments.py once the project is accepted.
    SIMULATED_PAYMENTS: bool = True
    HOSTEL_FEE_AMOUNT_INR: int = 60000

    RESERVATION_TTL_MINUTES: int = 15

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
