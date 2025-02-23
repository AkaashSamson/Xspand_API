from fastapi import APIRouter, Depends
from app.services.patient_service import PatientService
from app.models.schemas import Patient, SimplePatientRegistration, CompletePatientRegistration, XRayScan
from app.models.enums import TreatmentStatus
from app.database.firebase import FirebaseDB

router = APIRouter()

def get_patient_service():
    return PatientService(FirebaseDB())

@router.post("/register")
async def add_new_patient(registration: SimplePatientRegistration, service: PatientService = Depends(get_patient_service)):
    return await service.add_new_patient(registration)

@router.post("/register/complete")
async def register_complete_patient(
    registration: CompletePatientRegistration,
    patient_service: PatientService = Depends(get_patient_service)
):
    """
    Register a new patient with complete details and create a doctor-patient relationship.
    If the patient ID already exists or there's an ongoing relationship, appropriate error messages will be returned.
    """
    return await patient_service.register_complete_patient(registration)

@router.get("/status")
async def get_all_patients_status(service: PatientService = Depends(get_patient_service)):
    return await service.get_all_patients_status()

@router.put("/{patient_id}")
async def update_patient(patient_id: str, patient: dict, service: PatientService = Depends(get_patient_service)):
    return await service.update_patient(patient_id, patient)

@router.delete("/{patient_id}")
async def delete_patient(patient_id: str, service: PatientService = Depends(get_patient_service)):
    return await service.delete_patient(patient_id)

@router.get("/{patient_id}")
async def get_patient(patient_id: str, service: PatientService = Depends(get_patient_service)):
    return await service.get_patient(patient_id)

@router.get("/{patient_id}/complete")
async def get_patient_complete_details(
    patient_id: str,
    service: PatientService = Depends(get_patient_service)
):
    """
    Get complete patient details including:
    - Patient information
    - Current doctor details (if there's an ongoing treatment)
    - Current disease details (if diagnosed)
    """
    return await service.get_patient_complete_details(patient_id)

@router.get("/")
async def get_all_patients(service: PatientService = Depends(get_patient_service)):
    return await service.get_all_patients()



@router.get("/doctor/{doctor_id}")
async def get_doctor_patients(doctor_id: str, service: PatientService = Depends(get_patient_service)):
    return await service.get_doctor_patients(doctor_id)

@router.get("/doctor/current_patients/{doctor_id}")
async def get_doctor_patients(doctor_id: str, service: PatientService = Depends(get_patient_service)):
    return await service.get_current_doctor_patients(doctor_id)

@router.post("/xray")
async def add_xray_scan(scan: XRayScan, service: PatientService = Depends(get_patient_service)):
    return await service.add_xray_scan(scan)

@router.get("/{patient_id}/scans")
async def get_patient_scans(patient_id: str, service: PatientService = Depends(get_patient_service)):
    return await service.get_patient_scans(patient_id)

@router.put("/{patient_id}/treatment-status")
async def update_treatment_status(
    patient_id: str,
    doctor_id: str,
    status: TreatmentStatus,
    disease_id: str = None,
    service: PatientService = Depends(get_patient_service)
):
    return await service.update_treatment_status(doctor_id, patient_id, status, disease_id)

@router.put("/{patient_id}/treatment/{doctor_id}")
async def update_treatment(
    patient_id: str,
    doctor_id: str,
    treatment_data: dict,
    service: PatientService = Depends(get_patient_service)
):
    """
    Update treatment for a patient. Will update either:
    1. The ongoing treatment (where end_date is None), or
    2. The most recently completed treatment (with the latest end_date)
    """
    return await service.update_treatment(patient_id, doctor_id, treatment_data)
