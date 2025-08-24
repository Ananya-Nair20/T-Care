# backend/app/models/emergency_profile.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import uuid

class EmergencyProfile(Base):
    __tablename__ = "emergency_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), unique=True, nullable=False)
    qr_code_id = Column(String, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Medical Information
    medical_conditions = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    emergency_notes = Column(Text, nullable=True)
    
    # Emergency Contacts
    primary_contact_name = Column(String, nullable=True)
    primary_contact_phone = Column(String, nullable=True)
    secondary_contact_name = Column(String, nullable=True)
    secondary_contact_phone = Column(String, nullable=True)
    
    # Hospital Information
    preferred_hospital = Column(String, nullable=True)
    treating_doctor = Column(String, nullable=True)
    
    # QR Code
    qr_code_image = Column(Text, nullable=True)  # Base64 encoded image
    is_public = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="emergency_profile")