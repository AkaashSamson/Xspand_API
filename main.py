from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from fastapi import FastAPI, HTTPException
from firebase_admin import auth, firestore, credentials, initialize_app 
import uuid

app = FastAPI()
cred = credentials.Certificate(r'D:\Python_practs\Fast_API\fastapi_firebse_gcloud\fast_fire_crud\crudtest-1f1c5-firebase-adminsdk-f29ar-cb2dec6300.json')
initialize_app(cred)
db = firestore.client()

# Enums for predefined choices
class UserRole(str, Enum):
    admin = "Admin"
    doctor = "Doctor"
    radiologist = "Radiologist"

class Gender(str, Enum):
    male = "Male"
    female = "Female"

class TreatmentStatus(str, Enum):
    ongoing = "Ongoing"
    completed = "Completed"

class SeverityLevel(int, Enum):
    mild = 1
    moderate = 2
    severe = 3
    critical = 4

# Base User Model
class User(BaseModel):
    user_id: Optional[str] = None
    full_name: str
    email_address: str
    contact_number: str
    user_role: UserRole
    gender: Gender
    password: str


# Patient Model
class Patient(BaseModel):
    patient_id: str
    is_resident: bool
    full_name: Optional[str] = None
    email_address: Optional[str] = None
    contact_number: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    gender: Optional[Gender] = None


# Disease Model
class Disease(BaseModel):
    disease_id: str
    disease_name: str
    symptoms_list: List[str]
    severity_level: SeverityLevel
    specialist_required: str

# Doctor Model (inherits from User)
class Doctor(User):
    medical_specialization: str
    qualification_details: str
    years_of_experience: int

# Radiologist Model (inherits from User)
class Radiologist(User):
    expertise_domain: str
    years_of_experience: int

# Admin Model (inherits from User)
class Admin(User):
    admin_id: str

# X-Ray Scan Model
class XRayScan(BaseModel):
    scan_id: str
    patient_id: str
    doctor_id: Optional[str]
    radiologist_id: Optional[str]
    disease_id: Optional[str]
    ai_classification: Optional[str]
    no_findings_detected: bool
    radiologist_report: Optional[str]
    scan_timestamp: str

# Doctor-Patient Relationship Model
class Doc_Pat(BaseModel):
    doctor_id: str
    patient_id: str
    treatment_status: TreatmentStatus
    treatment_start_date: str
    treatment_end_date: Optional[str]
    diagnosed_with_disease: bool
    diagnosed_disease_id: Optional[str]


class RegisterRequest(BaseModel):
    role: UserRole
    email: str
    password: str


@app.post("/register")
def register_user(request: RegisterRequest):
    try:
        # Create Firebase Auth user
        user_record = auth.create_user(
            email=request.email,
            password=request.password
        )

        # Generate unique user_id
        user_id = user_record.uid

        # Store user details in Firestore
        user_data = {
            "user_id": user_id,
            "email_address": request.email,
            "user_role": request.role.value,
        }
        db.collection("users").document(user_record.uid).set(user_data)

        return {"message": "User registered successfully", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/register/doctor")
def register_doctor(request: Doctor):
    try:
        # Create Firebase Auth user
        user_record = auth.create_user(
            email=request.email_address,
            password=request.password
        )

        # Generate unique user_id
        user_id = user_record.uid

        # Store user details in Firestore
        user_data = request.dict()
        user_data["user_id"] = user_id
        db.collection("doctors").document(user_record.uid).set(user_data)

        return {"message": "Doctor registered successfully", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/register/radiologist")
async def register_radiologist(request: User):
    try:
        # Create Firebase Auth user
        user_record = auth.create_user(
            email=request.email_address,
            password=request.password
        )

        # Generate unique user_id
        user_id = user_record.uid

        # Store user details in Firestore
        user_data = request.dict()
        user_data["user_id"] = user_id
        user_data["user_role"] = UserRole.radiologist
        db.collection("radiologists").document(user_record.uid).set(user_data)

        return {"message": "Radiologist registered successfully", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/register/patient")
async def register_patient(request: Patient):
    try:
        # Generate unique patient_id using UUID
        patient_id = str(uuid.uuid4())
        
        # Store patient details in Firestore
        patient_data = request.dict()
        patient_data["patient_id"] = patient_id
        db.collection("patients").document(patient_id).set(patient_data)

        return {"message": "Patient registered successfully", "patient_id": patient_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/update/doctor/{doctor_id}")
async def update_doctor(doctor_id: str, request: Doctor):
    try:
        # Get the doctor document from Firestore
        doctor_ref = db.collection("doctors").document(doctor_id)
        doctor_data = doctor_ref.get().to_dict()

        # Update the doctor document with new data
        doctor_data.update(request.dict(exclude_unset=True))
        doctor_ref.set(doctor_data)

        return {"message": "Doctor updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/delete/doctor/{doctor_id}")
async def delete_doctor(doctor_id: str):
    try:
        # Delete the doctor document from Firestore
        doctor_ref = db.collection("doctors").document(doctor_id)
        doctor_ref.delete()

        # Delete the Firebase Auth user
        auth.delete_user(doctor_id)

        return {"message": "Doctor deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/update/patient/{patient_id}")
async def update_patient(patient_id: str, request: Patient):
    try:
        # Get the patient document from Firestore
        patient_ref = db.collection("patients").document(patient_id)
        patient_data = patient_ref.get().to_dict()

        # Update the patient document with new data
        patient_data.update(request.dict(exclude_unset=True))
        patient_ref.set(patient_data)

        return {"message": "Patient updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/delete/patient/{patient_id}")
async def delete_patient(patient_id: str):
    try:
        # Delete the patient document from Firestore
        patient_ref = db.collection("patients").document(patient_id)
        patient_ref.delete()

        return {"message": "Patient deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/update/radiologist/{radiologist_id}")
async def update_radiologist(radiologist_id: str, request: User):
    try:
        # Get the radiologist document from Firestore
        radiologist_ref = db.collection("radiologists").document(radiologist_id)
        radiologist_data = radiologist_ref.get().to_dict()

        # Update the radiologist document with new data
        radiologist_data.update(request.dict(exclude_unset=True))
        radiologist_ref.set(radiologist_data)

        return {"message": "Radiologist updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/delete/radiologist/{radiologist_id}")
async def delete_radiologist(radiologist_id: str):
    try:
        # Delete the radiologist document from Firestore
        radiologist_ref = db.collection("radiologists").document(radiologist_id)
        radiologist_ref.delete()

        # Delete the Firebase Auth user
        auth.delete_user(radiologist_id)

        return {"message": "Radiologist deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get/patients")
async def get_all_patients():
    try:
        # Get all the patient documents from Firestore
        patients_ref = db.collection("patients")
        patients = patients_ref.stream()
        patients_list = []
        for patient in patients:
            patients_list.append(patient.to_dict())
        return {"message": "Patients retrieved successfully", "patients": patients_list}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/get/doctors")
async def get_all_doctors():
    try:
        # Get all the doctor documents from Firestore
        doctors_ref = db.collection("doctors")
        doctors = doctors_ref.stream()
        doctors_list = []
        for doctor in doctors:
            doctors_list.append(doctor.to_dict())
        return {"message": "Doctors retrieved successfully", "doctors": doctors_list}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/get/radiologists")
async def get_all_radiologists():
    try:
        # Get all the radiologist documents from Firestore
        radiologists_ref = db.collection("radiologists")
        radiologists = radiologists_ref.stream()
        radiologists_list = []
        for radiologist in radiologists:
            radiologists_list.append(radiologist.to_dict())
        return {"message": "Radiologists retrieved successfully", "radiologists": radiologists_list}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
