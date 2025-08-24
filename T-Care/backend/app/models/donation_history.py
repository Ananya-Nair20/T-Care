# backend/app/models/donation_history.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class DonationHistory(Base):
    __tablename__ = "donation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    patient_id = Column(String, ForeignKey("users.user_id"), nullable=True)
    bridge_relationship_id = Column(Integer, ForeignKey("bridge_relationships.id"), nullable=True)
    
    # Donation details
    donation_date = Column(DateTime(timezone=True), nullable=True)  # allow missing
    quantity_ml = Column(Float, nullable=True)  # allow missing in CSV
    donation_type = Column(String, nullable=True)  # whole_blood, platelets, plasma
    
    # Location
    donation_center = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    donor = relationship("User", back_populates="donations", foreign_keys=[donor_id])
    patient = relationship("User", back_populates="received_donations", foreign_keys=[patient_id])
