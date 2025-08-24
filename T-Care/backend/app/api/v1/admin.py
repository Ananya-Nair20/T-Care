from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_stats():
    # TODO: Query real DB stats
    return {
        "total_patients": 42,
        "total_donors": 15,
        "matches_made": 27,
        "emergencies_handled": 5
    }
