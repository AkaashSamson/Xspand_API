from fastapi import FastAPI
from app.routes import user_routes, disease_routes, patient_routes, xray_routes
from app.config.firebase_config import init_firebase

# Initialize Firebase
init_firebase()

# Create FastAPI app
app = FastAPI(
    title="Xspand Medical System API",
    description="API for managing doctors, radiologists, patients, and diseases",
    version="1.0.0"
)

# Include routers
app.include_router(user_routes.router, prefix="/api/v1", tags=["users"])
app.include_router(disease_routes.router, prefix="/api/v1", tags=["diseases"])
app.include_router(patient_routes.router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(xray_routes.router, prefix="/api/v1/xrays", tags=["X-Ray Scans"])
