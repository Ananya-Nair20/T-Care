# backend/app/__init__.py

"""
T-Care Backend Application Package

This package contains the core backend logic for the T-Care platform,
including services for donor scheduling, gamification, emergency handling,
and data import.
"""

# Optional: expose main services at package level for convenience
from .services.data_import_service import DataImportService
from .services.emergency_service import DonorScheduler
from .services.gamification_service import GamificationService

__all__ = [
    "DataImportService",
    "DonorScheduler",
    "GamificationService",
]
