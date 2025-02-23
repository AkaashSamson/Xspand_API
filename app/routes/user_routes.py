from fastapi import APIRouter, Depends
from app.services.user_service import UserService
from app.models.schemas import Doctor, Radiologist, Patient
from app.database.firebase import FirebaseDB

router = APIRouter()

def get_user_service():
    return UserService(FirebaseDB())

# Doctor routes
@router.post("/register/doctor")
async def register_doctor(doctor: Doctor, service: UserService = Depends(get_user_service)):
    return await service.register_doctor(doctor)

@router.put("/update/doctor/{doctor_id}")
async def update_doctor(doctor_id: str, doctor: dict, service: UserService = Depends(get_user_service)):
    return await service.update_doctor(doctor_id, doctor)

@router.delete("/delete/doctor/{doctor_id}")
async def delete_doctor(doctor_id: str, service: UserService = Depends(get_user_service)):
    return await service.delete_doctor(doctor_id)

@router.get("/doctors")
async def get_all_doctors(service: UserService = Depends(get_user_service)):
    return await service.get_all_doctors()

@router.get("/doctors/{doctor_id}")
async def get_doctor(doctor_id: str, service: UserService = Depends(get_user_service)):
    return await service.get_doctor(doctor_id)

# Radiologist routes
@router.post("/register/radiologist")
async def register_radiologist(radiologist: Radiologist, service: UserService = Depends(get_user_service)):
    return await service.register_radiologist(radiologist)

@router.put("/update/radiologist/{radiologist_id}")
async def update_radiologist(radiologist_id: str, radiologist: dict, service: UserService = Depends(get_user_service)):
    return await service.update_radiologist(radiologist_id, radiologist)

@router.delete("/delete/radiologist/{radiologist_id}")
async def delete_radiologist(radiologist_id: str, service: UserService = Depends(get_user_service)):
    return await service.delete_radiologist(radiologist_id)

@router.get("/radiologists")
async def get_all_radiologists(service: UserService = Depends(get_user_service)):
    return await service.get_all_radiologists()

@router.get("/radiologists/{radiologist_id}")
async def get_radiologist(radiologist_id: str, service: UserService = Depends(get_user_service)):
    return await service.get_radiologist(radiologist_id)



