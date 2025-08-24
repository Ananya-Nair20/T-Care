import os
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "hackathon_data.csv"
)

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon points in km"""
    R = 6371  # km
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def normalize_blood_group(bg: str) -> str:
    if not isinstance(bg, str):
        return ""
    bg = bg.strip().upper()
    mapping = {
        "A POSITIVE": "A+", "A+": "A+", "A NEGATIVE": "A-", "A-": "A-",
        "B POSITIVE": "B+", "B+": "B+", "B NEGATIVE": "B-", "B-": "B-",
        "AB POSITIVE": "AB+", "AB+": "AB+", "AB NEGATIVE": "AB-", "AB-": "AB-",
        "O POSITIVE": "O+", "O+": "O+", "O NEGATIVE": "O-", "O-": "O-"
    }
    return mapping.get(bg, bg)

def load_data():
    """Load CSV and normalize blood groups"""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"CSV not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df["blood_group"] = df["blood_group"].apply(normalize_blood_group)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["next_eligible_date"] = pd.to_datetime(df["next_eligible_date"], errors="coerce")
    return df

class DonorScheduler:
    def __init__(self):
        self.df = load_data()
        # Keep track of scheduled donors
        self.scheduled_donors = {}  # {donor_id: list of scheduled dates}

    def _eligible_donors(self, blood_group):
        return self.df[
            (self.df["blood_group"] == blood_group) &
            (self.df["eligibility_status"].str.lower() == "eligible") &
            (self.df["latitude"].notna()) &
            (self.df["longitude"].notna())
        ]

    def emergency_donors(self, patient_lat, patient_lon, blood_group, top_n=10):
        """Return top N closest donors for emergencies"""
        donors = self._eligible_donors(blood_group)
        donors_list = []
        for _, row in donors.iterrows():
            distance = haversine(patient_lat, patient_lon, row["latitude"], row["longitude"])
            donors_list.append({
                "user_id": row["user_id"],
                "blood_group": row["blood_group"],
                "distance_km": round(distance, 2),
                "gender": row["gender"]
            })
        donors_sorted = sorted(donors_list, key=lambda x: x["distance_km"])
        return donors_sorted[:top_n]

    def schedule_regular_transfusion(self, patient_id, patient_lat, patient_lon, blood_group, transfusion_date, units_needed=1):
        """Schedule donors a day before transfusion ensuring no overlaps"""
        donors = self._eligible_donors(blood_group)
        # Sort donors by distance, availability and past reliability
        donors = donors.sort_values(by=["donations_till_date", "latitude"], ascending=[False, True])
        
        scheduled_date = transfusion_date - timedelta(days=1)
        assigned = []
        for _, row in donors.iterrows():
            donor_id = row["user_id"]
            # Skip if donor already scheduled on this date
            if donor_id in self.scheduled_donors and scheduled_date in self.scheduled_donors[donor_id]:
                continue
            assigned.append({
                "donor_id": donor_id,
                "blood_group": row["blood_group"],
                "distance_km": round(haversine(patient_lat, patient_lon, row["latitude"], row["longitude"]), 2),
                "scheduled_date": scheduled_date.strftime("%Y-%m-%d")
            })
            # Update schedule
            self.scheduled_donors.setdefault(donor_id, []).append(scheduled_date)
            if len(assigned) >= units_needed:
                break
        return assigned

if __name__ == "__main__":
    scheduler = DonorScheduler()
    # Example emergency donors
    emergency = scheduler.emergency_donors(28.6139, 77.2090, "A+", top_n=10)
    print("Emergency donors:", emergency)
    
    # Example regular transfusion scheduling
    transfusion_date = datetime(2025, 9, 1)
    schedule = scheduler.schedule_regular_transfusion(
        patient_id="P1",
        patient_lat=28.6139,
        patient_lon=77.2090,
        blood_group="A+",
        transfusion_date=transfusion_date,
        units_needed=2
    )
    print("Scheduled donors for transfusion:", schedule)
