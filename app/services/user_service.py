from app.database.firebase import FirebaseDB
from app.models.schemas import User, Doctor, Radiologist
import uuid
from fastapi import HTTPException

class UserService:
    def __init__(self, db: FirebaseDB):
        self.db = db

    async def register_doctor(self, doctor: Doctor):
        user_id = await self.db.create_user_auth(doctor.email_address, doctor.password)
        doctor_data = doctor.dict()
        doctor_data["user_id"] = user_id
        await self.db.create_document("doctors", user_id, doctor_data)
        return {"message": "Doctor registered successfully", "user_id": user_id}

    async def register_radiologist(self, radiologist: Radiologist):
        user_id = await self.db.create_user_auth(radiologist.email_address, radiologist.password)
        radiologist_data = radiologist.dict()
        radiologist_data["user_id"] = user_id
        await self.db.create_document("radiologists", user_id, radiologist_data)
        return {"message": "Radiologist registered successfully", "user_id": user_id}

    async def update_doctor(self, doctor_id: str, doctor: dict):
        doctor_exists = await self.db.get_document("doctors", doctor_id)
        if not doctor_exists:
            raise HTTPException(
            status_code=404,
            detail="Doctor not found"
            )
        try:
            await self.db.update_document("doctors", doctor_id, doctor)
            return {"message": "Doctor updated successfully"}
        except Exception as e:
            raise HTTPException(
            status_code=400,
            detail=f"Error updating doctor: {str(e)}"
            )

    async def update_radiologist(self, radiologist_id: str, radiologist: dict):
        radiologist_exists = await self.db.get_document("radiologists", radiologist_id)
        if not radiologist_exists:
            raise HTTPException(
            status_code=404,
            detail="Radiologist not found"
            )
        try:
            await self.db.update_document("radiologists", radiologist_id, radiologist)
            return {"message": "Radiologist updated successfully"}
        except Exception as e:
            raise HTTPException(
            status_code=400,
            detail=f"Error updating radiologist: {str(e)}"
            )

    async def delete_doctor(self, doctor_id: str):
        try:
            # First, get all doctor-patient relationships
            relations = await self.db.get_all_documents("doctor_patient_relations")
            doctor_relations = [r for r in relations if r.get("doctor_id") == doctor_id]
            
            # Delete all doctor-patient relationships
            for relation in doctor_relations:
                relation_id = f"{doctor_id}_{relation['patient_id']}"
                await self.db.delete_document("doctor_patient_relations", relation_id)
            
            # Delete from Firestore
            await self.db.delete_document("doctors", doctor_id)
            
            # Delete from Firebase Auth
            await self.db.delete_user_auth(doctor_id)
            
            return {"message": "Doctor and all related records deleted successfully"}
            
        except Exception as e:
            # If deletion from auth fails, we should try to rollback Firestore deletion
            raise HTTPException(
                status_code=400,
                detail=f"Error deleting doctor: {str(e)}"
            )

    async def delete_radiologist(self, radiologist_id: str):
        try:
            # Get all X-ray scans by this radiologist
            scans = await self.db.get_all_documents("xray_scans")
            radiologist_scans = [s for s in scans if s.get("radiologist_id") == radiologist_id]
            
            # Update all scans to remove radiologist reference
            for scan in radiologist_scans:
                scan_data = {
                    "radiologist_id": None,
                    "radiologist_report": None
                }
                await self.db.update_document("xray_scans", scan["scan_id"], scan_data)
            
            # Delete from Firestore
            await self.db.delete_document("radiologists", radiologist_id)
            
            # Delete from Firebase Auth
            await self.db.delete_user_auth(radiologist_id)
            
            return {"message": "Radiologist deleted successfully and scans updated"}
            
        except Exception as e:
            # If deletion from auth fails, we should try to rollback Firestore deletion
            raise HTTPException(
                status_code=400,
                detail=f"Error deleting radiologist: {str(e)}"
            )

    async def get_all_doctors(self):
        doctors = await self.db.get_all_documents("doctors")
        return {"message": "Doctors retrieved successfully", "doctors": doctors}

    async def get_all_radiologists(self):
        radiologists = await self.db.get_all_documents("radiologists")
        return {"message": "Radiologists retrieved successfully", "radiologists": radiologists}

    
    async def get_doctor(self, doctor_id: str):
        doctor = await self.db.get_document("doctors", doctor_id)
        if doctor:
            return {"message": "Doctor retrieved successfully", "doctor": doctor}
        else:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )

    async def get_radiologist(self, radiologist_id: str):
        radiologist = await self.db.get_document("radiologists", radiologist_id)
        if radiologist:
            return {"message": "Radiologist retrieved successfully", "radiologist": radiologist}
        else:
            raise HTTPException(
                status_code=404,
                detail="Radiologist not found"
            )
