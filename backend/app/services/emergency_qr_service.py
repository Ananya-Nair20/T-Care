import qrcode
import io
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import os
from math import radians, sin, cos, sqrt, atan2

# Path to CSV database
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "hackathon_data.csv")

# Load CSV
def load_donors():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV not found at {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    # Normalize blood group
    df["blood_group"] = df["blood_group"].str.upper()
    df["user_id"] = df["user_id"].astype(str)
    return df

donors_df = load_donors()
app = FastAPI(title="Emergency QR Profile System")

def generate_qr_code(data: str):
    """Generates a QR code image as PNG bytes"""
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def haversine(lat1, lon1, lat2, lon2):
    """Distance in km between two lat/lon points"""
    R = 6371
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2)**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    return R * c

def get_nearby_emergency_donors(blood_group: str, lat: float, lon: float, top_n: int = 5):
    df = donors_df[(donors_df["blood_group"] == blood_group.upper()) &
                   (donors_df["eligibility_status"].astype(str).str.lower() == "eligible")]
    nearby = []
    for _, row in df.iterrows():
        if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
            continue
        distance = haversine(lat, lon, row["latitude"], row["longitude"])
        nearby.append({
            "user_id": row["user_id"],
            "blood_group": row["blood_group"],
            "distance_km": round(distance, 2),
            "gender": row.get("gender", "Unknown")
        })
    nearby_sorted = sorted(nearby, key=lambda x: x["distance_km"])
    return nearby_sorted[:top_n]

@app.get("/emergency_qr/{user_id}")
def emergency_qr(user_id: str):
    """
    Generates a QR code for a donor's emergency profile.
    QR encodes a link to their public profile.
    """
    if user_id not in donors_df["user_id"].values:
        raise HTTPException(status_code=404, detail="User not found")
    profile_url = f"https://tcare.app/emergency_profile/{user_id}"
    img_buf = generate_qr_code(profile_url)
    return StreamingResponse(img_buf, media_type="image/png")

@app.get("/emergency_profile/{user_id}")
def emergency_profile(user_id: str):
    """
    Returns the public emergency info for a donor.
    No login required. Includes nearby emergency donors.
    """
    donor = donors_df[donors_df["user_id"] == user_id]
    if donor.empty:
        raise HTTPException(status_code=404, detail="User not found")

    donor_info = donor.iloc[0]
    profile = {
        "user_id": donor_info["user_id"],
        "blood_group": donor_info["blood_group"],
        "allergies": donor_info.get("allergies", "None"),
        "last_transfusion_date": donor_info.get("last_transfusion_date", "Unknown"),
        "emergency_contacts": donor_info.get("emergency_contacts", "Unknown"),
        "gender": donor_info.get("gender", "Unknown"),
        "age": donor_info.get("age", "Unknown")
    }

    # Add top nearby emergency donors
    lat = donor_info.get("latitude")
    lon = donor_info.get("longitude")
    if pd.notna(lat) and pd.notna(lon):
        profile["nearby_emergency_donors"] = get_nearby_emergency_donors(
            blood_group=donor_info["blood_group"], lat=lat, lon=lon, top_n=5
        )
    else:
        profile["nearby_emergency_donors"] = []

    return JSONResponse(content=profile)

@app.get("/emergency_nearby")
def emergency_nearby(blood_group: str, lat: float, lon: float, top_n: int = 10):
    """
    Returns top N nearby eligible donors for emergencies.
    """
    return get_nearby_emergency_donors(blood_group, lat, lon, top_n)
