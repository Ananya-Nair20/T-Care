from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(prefix="/donors", tags=["donors"])

# ----------------------
# Data Models
# ----------------------

class Donor(BaseModel):
    id: int
    name: str
    blood_type: str
    available_units: int = Field(..., ge=0, description="Number of blood units donor can provide")
    contact: Optional[str] = None

class DonorCreate(BaseModel):
    name: str
    blood_type: str
    available_units: int = Field(..., ge=0)
    contact: Optional[str] = None

class MatchRequest(BaseModel):
    patient_blood_type: str
    required_units: int = Field(..., ge=1)

class MatchResult(BaseModel):
    donor_id: int
    donor_name: str
    units_matched: int

# ----------------------
# Mock Database
# ----------------------
donors_db: List[Donor] = [
    Donor(id=1, name="John Doe", blood_type="O+", available_units=5, contact="1234567890"),
    Donor(id=2, name="Jane Smith", blood_type="A-", available_units=2, contact="9876543210"),
]

# ----------------------
# Endpoints
# ----------------------

@router.get("/", response_model=List[Donor])
async def list_donors():
    """Get a list of all donors."""
    return donors_db


@router.post("/", response_model=Donor)
async def create_donor(donor: DonorCreate):
    """Register a new donor."""
    new_donor = Donor(
        id=len(donors_db) + 1,
        name=donor.name,
        blood_type=donor.blood_type,
        available_units=donor.available_units,
        contact=donor.contact,
    )
    donors_db.append(new_donor)
    return new_donor


@router.post("/match", response_model=MatchResult)
async def find_match(request: MatchRequest):
    """Find a matching donor for the patient."""
    # Simplified matching: look for same blood type and enough units
    for donor in donors_db:
        if donor.blood_type == request.patient_blood_type and donor.available_units >= request.required_units:
            return MatchResult(
                donor_id=donor.id,
                donor_name=donor.name,
                units_matched=request.required_units
            )

    raise HTTPException(status_code=404, detail="No matching donor found")
