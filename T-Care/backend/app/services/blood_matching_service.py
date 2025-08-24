from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import math
from ..models.user import User, BloodGroup
from ..database import get_db
from ..models.bridge_relationship import BridgeRelationship
from ..config import settings


class BloodMatchingService:
    """
    Core service for AI-powered blood matching between patients and donors.
    Uses Haversine distance formula for geographic matching and 
    multi-factor scoring for optimal donor selection.
    """
    
    # Blood compatibility matrix
    BLOOD_COMPATIBILITY = {
        "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
        "O+": ["O+", "A+", "B+", "AB+"],
        "A-": ["A-", "A+", "AB-", "AB+"],
        "A+": ["A+", "AB+"],
        "B-": ["B-", "B+", "AB-", "AB+"],
        "B+": ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"]
    }
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance (km) between two geo coordinates"""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return 6371 * c  # km
    
    @classmethod
    def get_compatible_blood_groups(cls, patient_blood_group: str) -> List[str]:
        """Return compatible donor blood groups for a patient"""
        compatible_donors = []
        for donor_group, can_donate_to in cls.BLOOD_COMPATIBILITY.items():
            if patient_blood_group in can_donate_to:
                compatible_donors.append(donor_group)
        return compatible_donors
    
    @classmethod
    def calculate_donor_score(cls, donor: User, patient: User, distance_km: float) -> float:
        """Calculate donor-patient matching score"""
        score = 0.0

        # 1. Blood compatibility (40%)
        compatible_groups = cls.get_compatible_blood_groups(patient.blood_group.value)
        if donor.blood_group.value in compatible_groups:
            compatibility_score = 1.0 if donor.blood_group.value == patient.blood_group.value else 0.8
        else:
            return 0.0
        score += compatibility_score * settings.COMPATIBILITY_WEIGHT

        # 2. Distance (30%)
        distance_score = 1.0 - (distance_km / settings.MAX_DISTANCE_KM) if distance_km <= settings.MAX_DISTANCE_KM else 0.0
        score += distance_score * settings.DISTANCE_WEIGHT

        # 3. Availability (20%)
        availability_score = 0.0
        if donor.eligibility_status == "eligible":
            availability_score = 1.0
        elif donor.next_eligible_date:
            days_until_eligible = (donor.next_eligible_date - datetime.now().date()).days
            if days_until_eligible <= 7:
                availability_score = 0.5
        score += availability_score * settings.AVAILABILITY_WEIGHT

        # 4. Engagement (10%)
        engagement_score = 0.0
        if donor.donations_till_date:
            if donor.donations_till_date >= 10:
                engagement_score = 1.0
            elif donor.donations_till_date >= 5:
                engagement_score = 0.7
            elif donor.donations_till_date >= 1:
                engagement_score = 0.5

        if donor.calls_to_donations_ratio and donor.calls_to_donations_ratio > 0:
            if donor.calls_to_donations_ratio <= 2:
                engagement_score = min(engagement_score + 0.3, 1.0)
        score += engagement_score * settings.ENGAGEMENT_WEIGHT

        return score
    
    @classmethod
    def find_matching_donors(cls, db: Session, patient_id: str, limit: int = 10, emergency: bool = False) -> List[Dict]:
        """Return top donor matches for a patient"""
        patient = db.query(User).filter(User.user_id == patient_id).first()
        if not patient:
            return []

        compatible_groups = cls.get_compatible_blood_groups(patient.blood_group.value)
        query = db.query(User).filter(
            and_(
                User.role == "donor",
                User.blood_group.in_(compatible_groups),
                User.user_donation_active_status != "inactive"
            )
        )
        if emergency:
            query = query.filter(User.eligibility_status == "eligible")

        potential_donors = query.all()
        donor_scores = []

        for donor in potential_donors:
            if not (donor.latitude and donor.longitude and patient.latitude and patient.longitude):
                continue
            distance = cls.haversine_distance(patient.latitude, patient.longitude, donor.latitude, donor.longitude)
            if not emergency and distance > settings.MAX_DISTANCE_KM:
                continue

            score = cls.calculate_donor_score(donor, patient, distance)
            if score > 0:
                donor_scores.append({
                    "donor": donor,
                    "score": score,
                    "distance_km": round(distance, 2),
                    "blood_group": donor.blood_group.value,
                    "eligibility_status": donor.eligibility_status,
                    "donations_count": donor.donations_till_date or 0,
                    "last_donation_date": donor.last_donation_date,
                    "next_eligible_date": donor.next_eligible_date
                })

        donor_scores.sort(key=lambda x: x["score"], reverse=True)
        return donor_scores[:limit]
    
    @classmethod
    def create_bridge_relationship(cls, db: Session, patient_id: str, donor_id: str, compatibility_score: float = None) -> BridgeRelationship:
        """Create a new patient-donor bridge if one doesn’t already exist"""
        existing = db.query(BridgeRelationship).filter(
            and_(
                BridgeRelationship.patient_id == patient_id,
                BridgeRelationship.donor_id == donor_id,
                BridgeRelationship.is_active == True
            )
        ).first()
        if existing:
            return existing

        bridge = BridgeRelationship(
            patient_id=patient_id,
            donor_id=donor_id,
            compatibility_score=compatibility_score,
            is_active=True
        )

        patient = db.query(User).filter(User.user_id == patient_id).first()
        donor = db.query(User).filter(User.user_id == donor_id).first()
        if patient:
            patient.bridge_status = True
            patient.status_of_bridge = True
        if donor:
            donor.bridge_status = True
            donor.status_of_bridge = True

        db.add(bridge)
        db.commit()
        db.refresh(bridge)
        return bridge
    
    @classmethod
    def get_patient_bridges(cls, db: Session, patient_id: str, active_only: bool = True) -> List[BridgeRelationship]:
        """Get patient’s bridge relationships"""
        query = db.query(BridgeRelationship).filter(BridgeRelationship.patient_id == patient_id)
        if active_only:
            query = query.filter(BridgeRelationship.is_active == True)
        return query.all()
    
    @classmethod
    def get_donor_bridges(cls, db: Session, donor_id: str, active_only: bool = True) -> List[BridgeRelationship]:
        """Get donor’s bridge relationships"""
        query = db.query(BridgeRelationship).filter(BridgeRelationship.donor_id == donor_id)
        if active_only:
            query = query.filter(BridgeRelationship.is_active == True)
        return query.all()
