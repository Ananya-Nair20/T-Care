from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Example schema
class Patient(BaseModel):
    id: int
    name: str
    age: int
    blood_type: str
    thalassemia_type: str

fake_patients: List[Patient] = []

@router.get("/", response_model=List[Patient])
async def list_patients():
    return fake_patients

@router.post("/", response_model=Patient)
async def create_patient(patient: Patient):
    fake_patients.append(patient)
    return patient

@router.get("/{patient_id}", response_model=Patient)
async def get_patient(patient_id: int):
    for p in fake_patients:
        if p.id == patient_id:
            return p
    raise HTTPException(status_code=404, detail="Patient not found")
