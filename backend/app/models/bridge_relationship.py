# backend/app/models/bridge_relationship.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class BridgeRelationship(Base):
    __tablename__ = "bridge_relationships"
    __table_args__ = (UniqueConstraint("patient_id", "donor_id", name="uq_patient_donor"),)

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    donor_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    bridge_id = Column(String, index=True)
    
    # Relationship status
    is_active = Column(Boolean, default=True)
    compatibility_score = Column(Float, nullable=True)
    
    # Scheduling
    next_transfusion_date = Column(DateTime(timezone=True), nullable=True)
    frequency_days = Column(Integer, nullable=True)
    
    # Tracking
    total_donations = Column(Integer, default=0)
    last_donation_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("User", back_populates="bridge_relationships", foreign_keys=[patient_id])
    donor = relationship("User", back_populates="donor_relationships", foreign_keys=[donor_id])
    