"""
Application configuration using pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENV: str = Field(default="local", description="Environment: local, dev, prod")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Kernel API
    KERNEL_API_KEY: str = Field(..., description="Kernel API key")
    
    # Database
    DATABASE_URL: str = Field(..., description="Database connection URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Application settings
    DEFAULT_STEALTH: bool = Field(default=True, description="Default stealth mode for browsers")
    MAX_CONCURRENCY: int = Field(default=10, description="Maximum concurrent runs")
    
    # API settings
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8080, description="API port")
    
    # Worker settings
    WORKER_CONCURRENCY: int = Field(default=4, description="Worker concurrency")
    JOB_TIMEOUT: int = Field(default=300, description="Job timeout in seconds")
    
    # Friction analysis settings
    FRICTION_THRESHOLD: float = Field(default=0.7, description="Friction score threshold")
    LONG_DWELL_THRESHOLD: int = Field(default=10, description="Long dwell threshold in seconds")
    RAGE_CLICK_THRESHOLD: int = Field(default=3, description="Rage click threshold")
    
    # Optional API keys for AI features
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="Google API key for AI features")
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key for AI features")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API key for AI features")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
