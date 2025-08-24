from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ...database import get_db
from ...services.blood_matching_service import BloodMatchingService
from ...models.user import User

router = APIRouter(prefix="/blood-matching", tags=["Blood Matching"])

# ----------------------
# Request & Response Models
# ----------------------

class DonorMatch(BaseModel):
    donor_id: str
    blood_group: str
    distance_km: float
    score: float
    eligibility_status: Optional[str] = None
    donations_count: int = 0
    last_donation_date: Optional[datetime] = None
    next_eligible_date: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class MatchRequest(BaseModel):
    patient_id: str
    emergency: bool = False
    limit: int = 10

class BridgeRequest(BaseModel):
    patient_id: str
    donor_id: str

# ----------------------
# Endpoints
# ----------------------

@router.post("/find-donors", response_model=List[DonorMatch])
async def find_matching_donors(request: MatchRequest, db: Session = Depends(get_db)):
    """
    Find best matching donors for a patient using AI-powered algorithm.
    """
    try:
        matches = BloodMatchingService.find_matching_donors(
            db=db,
            patient_id=request.patient_id,
            limit=request.limit,
            emergency=request.emergency
        )
        result = []
        for match in matches:
            donor = match["donor"]
            result.append(DonorMatch(
                donor_id=donor.user_id,
                blood_group=match.get("blood_group", ""),
                distance_km=match.get("distance_km", 0.0),
                score=match.get("score", 0.0),
                eligibility_status=match.get("eligibility_status"),
                donations_count=match.get("donations_count", 0),
                last_donation_date=match.get("last_donation_date"),
                next_eligible_date=match.get("next_eligible_date"),
                latitude=getattr(donor, "latitude", None),
                longitude=getattr(donor, "longitude", None)
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-bridge")
async def create_bridge_relationship(request: BridgeRequest, db: Session = Depends(get_db)):
    """
    Create a bridge relationship between a patient and a donor.
    """
    try:
        bridge = BloodMatchingService.create_bridge_relationship(
            db=db,
            patient_id=request.patient_id,
            donor_id=request.donor_id
        )
        return {
            "success": True,
            "bridge_id": bridge.id,
            "message": "Bridge relationship created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patient-bridges/{patient_id}")
async def get_patient_bridges(patient_id: str, active_only: bool = Query(True), db: Session = Depends(get_db)):
    """
    Get all bridge relationships for a patient.
    """
    try:
        bridges = BloodMatchingService.get_patient_bridges(db=db, patient_id=patient_id, active_only=active_only)
        result = []
        for bridge in bridges:
            donor = bridge.donor
            result.append({
                "bridge_id": bridge.id,
                "donor_id": donor.user_id,
                "donor_blood_group": getattr(donor.blood_group, "value", None),
                "is_active": bridge.is_active,
                "total_donations": getattr(bridge, "total_donations", 0),
                "last_donation_date": getattr(bridge, "last_donation_date", None),
                "next_transfusion_date": getattr(bridge, "next_transfusion_date", None)
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/donor-bridges/{donor_id}")
async def get_donor_bridges(donor_id: str, active_only: bool = Query(True), db: Session = Depends(get_db)):
    """
    Get all bridge relationships for a donor.
    """
    try:
        bridges = BloodMatchingService.get_donor_bridges(db=db, donor_id=donor_id, active_only=active_only)
        result = []
        for bridge in bridges:
            patient = bridge.patient
            result.append({
                "bridge_id": bridge.id,
                "patient_id": patient.user_id,
                "patient_blood_group": getattr(patient.blood_group, "value", None),
                "is_active": bridge.is_active,
                "total_donations": getattr(bridge, "total_donations", 0),
                "last_donation_date": getattr(bridge, "last_donation_date", None),
                "next_transfusion_date": getattr(bridge, "next_transfusion_date", None)
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compatibility/{blood_group}")
async def get_compatible_blood_groups(blood_group: str):
    """
    Get compatible blood groups for donation.
    """
    try:
        compatible = BloodMatchingService.get_compatible_blood_groups(blood_group)
        return {
            "patient_blood_group": blood_group,
            "compatible_donor_groups": compatible
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
