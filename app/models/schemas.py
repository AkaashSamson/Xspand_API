from pydantic import BaseModel
from typing import Optional, List
from app.models.enums import TreatmentStatus, Gender, UserRole, SeverityLevel

class User(BaseModel):
    user_id: Optional[str] = None
    email: str
    role: UserRole

class Doctor(User):
    doctor_id: Optional[str] = None
    full_name: str
    specialization: str

class Radiologist(User):
    radiologist_id: Optional[str] = None
    full_name: str
    specialization: str

class Patient(BaseModel):
    patient_id: str
    full_name: str
    is_resident: bool
    email_address: str
    contact_number: str
    age: int
    height_cm: float
    weight_kg: float
    gender: Gender

class PatientRegistration(BaseModel):
    patient: Patient
    doctor_id: str

class SimplePatientRegistration(BaseModel):
    patient_id: str
    doctor_id: str
    is_resident: bool

class CompletePatientRegistration(BaseModel):
    patient_id: str
    doctor_id: str
    full_name: str
    is_resident: bool
    email_address: str
    contact_number: str
    age: int
    height_cm: float
    weight_kg: float
    gender: Gender

class Disease(BaseModel):
    disease_id: Optional[str] = None
    disease_name: str
    description: str
    severity_level: SeverityLevel
    common_symptoms: List[str]
    treatment_methods: List[str]

class Admin(User):
    admin_id: str

class XRayScan(BaseModel):
    image_url: str
    scan_id: Optional[str] = None
    patient_id: str
    doctor_id: str
    radiologist_id: Optional[str] = None
    disease_id: Optional[str] = None
    ai_classification: Optional[str] = None
    no_findings_detected: Optional[bool] = None
    radiologist_report: Optional[str] = None
    scan_timestamp: Optional[str] = None
    disease_name: Optional[str] = None
    ai_approved: Optional[bool] = False

class DoctorPatientRelation(BaseModel):
    doctor_id: str
    patient_id: str
    treatment_status: TreatmentStatus
    treatment_start_date: str
    treatment_end_date: Optional[str]
    diagnosed_with_disease: bool
    diagnosed_disease_id: Optional[str]
