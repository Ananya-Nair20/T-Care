# backend/app/models/user.py
from sqlalchemy import Column, String, Float, Boolean, Date, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class UserRole(str, enum.Enum):
    PATIENT = "PATIENT"
    DONOR = "DONOR"
    VOLUNTEER = "VOLUNTEER"
    ADMIN = "ADMIN"
    GUEST = "GUEST"

class BloodGroup(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class User(Base):
    __tablename__ = "users"
    
    # Primary fields from CSV
    user_id = Column(String, primary_key=True, index=True)
    bridge_id = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    role_status = Column(Boolean, default=True)
    bridge_status = Column(Boolean, default=False)
    
    # Personal Information
    blood_group = Column(SQLEnum(BloodGroup), nullable=True)  # allow missing in CSV
    gender = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Bridge Information
    bridge_gender = Column(String, nullable=True)
    bridge_blood_group = Column(String, nullable=True)
    
    # Patient-specific fields
    quantity_required = Column(Float, nullable=True)
    last_transfusion_date = Column(Date, nullable=True)
    expected_next_transfusion_date = Column(Date, nullable=True)
    
    # Donor-specific fields
    donor_type = Column(String, nullable=True)
    last_contacted_date = Column(Date, nullable=True)
    last_donation_date = Column(Date, nullable=True)
    next_eligible_date = Column(Date, nullable=True)
    donations_till_date = Column(Float, default=0)
    eligibility_status = Column(String, nullable=True)
    cycle_of_donations = Column(Integer, default=0)
    total_calls = Column(Integer, default=0)
    frequency_in_days = Column(Integer, nullable=True)
    
    # Status fields
    status_of_bridge = Column(Boolean, default=False)
    status = Column(String, nullable=True)
    donated_earlier = Column(String, nullable=True)
    last_bridge_donation_date = Column(Date, nullable=True)
    calls_to_donations_ratio = Column(Float, nullable=True)
    user_donation_active_status = Column(String, nullable=True)
    inactive_trigger_comment = Column(String, nullable=True)
    
    # System fields
    registration_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Authentication (for future use)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    
    # Relationships
    bridge_relationships = relationship("BridgeRelationship", back_populates="patient", foreign_keys="BridgeRelationship.patient_id")
    donor_relationships = relationship("BridgeRelationship", back_populates="donor", foreign_keys="BridgeRelationship.donor_id")
    donations = relationship("DonationHistory", back_populates="donor", foreign_keys="DonationHistory.donor_id")
    received_donations = relationship("DonationHistory", back_populates="patient", foreign_keys="DonationHistory.patient_id")
    emergency_profile = relationship("EmergencyProfile", back_populates="user", uselist=False)
    gamification_profile = relationship("GamificationProfile", back_populates="user", uselist=False)