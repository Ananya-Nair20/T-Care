from fastapi import APIRouter
from pydantic import BaseModel
import datetime

router = APIRouter()

class EmergencyAlert(BaseModel):
    patient_id: int
    location: str
    required_units: int
    timestamp: datetime.datetime

@router.post("/alert")
async def send_alert(alert: EmergencyAlert):
    # TODO: Notify hospitals/donors
    return {"message": "Emergency alert sent", "details": alert}
