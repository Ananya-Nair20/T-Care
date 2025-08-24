# backend/app/api/v1/donor_scheduler.py
from fastapi import APIRouter, Query
from datetime import datetime
from ...services.donor_scheduler_service import DonorScheduler

router = APIRouter()
scheduler = DonorScheduler()

@router.get("/emergency-donors")
def get_emergency_donors(
    lat: float = Query(...), lon: float = Query(...), blood_group: str = Query(...), top_n: int = 10
):
    return scheduler.emergency_donors(lat, lon, blood_group, top_n)

@router.get("/scheduled-donors")
def get_scheduled_donors(
    patient_id: str = Query(...),
    lat: float = Query(...),
    lon: float = Query(...),
    blood_group: str = Query(...),
    transfusion_date: str = Query(...),
    units_needed: int = Query(1)
):
    transfusion_dt = datetime.fromisoformat(transfusion_date)
    return scheduler.schedule_regular_transfusion(
        patient_id, lat, lon, blood_group, transfusion_dt, units_needed
    )
