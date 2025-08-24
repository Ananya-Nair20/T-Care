# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="T-Care Backend", version="1.0.0")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # you can restrict to ["http://localhost:3000"] later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "T-Care backend is running 🚀"}

# Example health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Import and include routers here ---
# from routes import auth, patients, donors, matching, forum
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
# app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
# app.include_router(donors.router, prefix="/api/v1/donors", tags=["Donors"])
# app.include_router(matching.router, prefix="/api/v1/matching", tags=["Matching"])
# app.include_router(forum.router, prefix="/api/v1/forum", tags=["Forum"])
