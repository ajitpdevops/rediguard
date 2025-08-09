"""Core configuration for Rediguard backend"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Redis Stack features
    redis_stream_maxlen: int = 10000
    vector_dimension: int = 128
    anomaly_threshold: float = 0.8
    
    # API Configuration
    api_title: str = "Rediguard API"
    api_description: str = "Real-Time Security & Threat Detection MVP"
    api_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    
    # AI Model Configuration
    ai_model_type: str = "isolation_forest"
    contamination_rate: float = 0.1
    
    # Processing Configuration
    stream_consumer_group: str = "security_processors"
    stream_consumer_name: str = "processor_01"
    
    # Geographic distance threshold (km)
    geo_jump_threshold: float = 1000.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
