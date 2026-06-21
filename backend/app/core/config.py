from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Core Infrastructure Framework Configurations
    PROJECT_NAME: str = "Enterprise Knowledge Intelligence API"
    API_V1_STR: str = "/api/v1"
    
    # PRODUCTION TARGET: Reads the standalone PostgreSQL connection string from Docker environment parameters
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:enterprise_password_2026@db:5432/enterprise_db"
    )
    
    # ISOLATED VECTOR INDEX PATH: Separated completely from other service roots
    CHROMA_PERSIST_DIR: str = "/app/chroma_vector_db"
    
    # Environment property pulling your Gemini API key from the local environment bindings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Cryptographic Authentication Security Metrics Keys
    SECRET_KEY: str = "SUPER_SECRET_COMPUTE_MATRIX_KEY_2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # Session active lifetime duration: 7 Days

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()