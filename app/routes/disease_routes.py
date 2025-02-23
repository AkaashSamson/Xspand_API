from fastapi import APIRouter, Depends
from app.services.disease_service import DiseaseService
from app.models.schemas import Disease
from app.database.firebase import FirebaseDB

router = APIRouter()

def get_disease_service():
    return DiseaseService(FirebaseDB())

@router.post("/diseases")
async def add_disease(disease: Disease, service: DiseaseService = Depends(get_disease_service)):
    return await service.add_disease(disease)

@router.put("/diseases/{disease_id}")
async def update_disease(disease_id: str, disease: dict, service: DiseaseService = Depends(get_disease_service)):
    return await service.update_disease(disease_id, disease)

@router.delete("/diseases/{disease_id}")
async def delete_disease(disease_id: str, service: DiseaseService = Depends(get_disease_service)):
    return await service.delete_disease(disease_id)

@router.get("/diseases")
async def get_all_diseases(service: DiseaseService = Depends(get_disease_service)):
    return await service.get_all_diseases()

@router.get("/diseases/{disease_id}")
async def get_disease(disease_id: str, service: DiseaseService = Depends(get_disease_service)):
    return await service.get_disease(disease_id)

@router.get("/diseases/counts/all_patients")
async def get_disease_patient_counts(service: DiseaseService = Depends(get_disease_service)):
    return await service.get_all_disease_patient_counts()

@router.get("/diseases/counts/current_patients")
async def get_disease_patient_counts(service: DiseaseService = Depends(get_disease_service)):
    return await service.get_disease_patient_counts()
