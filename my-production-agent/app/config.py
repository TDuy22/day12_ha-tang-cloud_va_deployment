from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Cài đặt mặc định nếu không có biến môi trường
    port: int = 8000
    redis_url: str = "redis://localhost:6379"
    
    # Ở môi trường production, key này bắt buộc phải sửa trong file .env
    agent_api_key: str = "default-secret-key"
    log_level: str = "INFO"
    
    # Định mức phòng hộ (Rate Limiter & Cost Guard)
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    
    # Kích hoạt thực tế OpenAI
    openai_api_key: str

    class Config:
        env_file = ".env" # Bảo code quét tìm file .env

settings = Settings()
