# backend/scripts/seed_data.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.services.data_import_service import DataImportService
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def seed_data():
    """Seed database with CSV data"""
    db = SessionLocal()
    try:
        logger.info("Starting data seeding process...")
        
        # Import data from CSV
        stats = DataImportService.import_from_csv(db)
        
        logger.info("Data seeding completed successfully!")
        logger.info(f"Statistics: {stats}")
        
    except Exception as e:
        logger.error(f"Error during data seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    seed_data()