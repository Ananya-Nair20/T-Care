from pydantic_settings import BaseSettings
from typing import List, Dict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/tcare_db"
    CSV_FILE_PATH="/home/nidhi/T-Care/T-Care/data/hackathon_data.csv"

    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    APP_NAME: str = "T-Care Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Emergency System
    EMERGENCY_QR_BASE_URL: str = "http://localhost:3000/emergency/profile/"
    
    # Blood Matching Parameters
    MAX_DISTANCE_KM: float = 50.0
    COMPATIBILITY_WEIGHT: float = 0.4
    DISTANCE_WEIGHT: float = 0.3
    AVAILABILITY_WEIGHT: float = 0.2
    ENGAGEMENT_WEIGHT: float = 0.1
    
    # Gamification Settings
    DONATION_POINTS: int = 100
    MILESTONE_DONATIONS: List[int] = [5, 10, 25, 50, 100]
    BADGE_THRESHOLDS: Dict[str, int] = {
        "bronze": 5,
        "silver": 10,
        "gold": 25,
        "platinum": 50,
        "diamond": 100,
    }
    
    # Data Import
    CSV_FILE_PATH: str = "./data/hackathon_data.csv"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
