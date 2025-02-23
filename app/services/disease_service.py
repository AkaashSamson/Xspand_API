from app.database.firebase import FirebaseDB
from app.models.schemas import Disease
import uuid

class DiseaseService:
    def __init__(self, db: FirebaseDB):
        self.db = db

    async def add_disease(self, disease: Disease):
        disease_id = str(uuid.uuid4())
        disease_data = disease.dict()
        disease_data["disease_id"] = disease_id
        await self.db.create_document("diseases", disease_id, disease_data)
        return {"message": "Disease added successfully", "disease_id": disease_id}

    async def update_disease(self, disease_id: str, disease: Disease):
        await self.db.update_document("diseases", disease_id, disease.dict(exclude_unset=True))
        return {"message": "Disease updated successfully"}

    async def delete_disease(self, disease_id: str):
        await self.db.delete_document("diseases", disease_id)
        return {"message": "Disease deleted successfully"}

    async def get_all_diseases(self):
        diseases = await self.db.get_all_documents("diseases")
        return {"message": "Diseases retrieved successfully", "diseases": diseases}

    async def get_disease(self, disease_id: str):
        disease = await self.db.get_document("diseases", disease_id)
        return {"message": "Disease retrieved successfully", "disease": disease}
    
    #for each disease find the no. of patients diagnosed with it
    async def get_all_disease_patient_counts(self):
        try:
            diseases = await self.db.get_all_documents("diseases")
        except Exception as e:
            return {"message": "Failed to retrieve diseases", "error": str(e), "function": "get_disease_patient_counts"}

        try:
            relations = await self.db.get_all_documents("doctor_patient_relations")
        except Exception as e:
            return {"message": "Failed to retrieve doctor-patient relations", "error": str(e), "function": "get_disease_patient_counts"}

        disease_patient_counts = []
        try:
            for disease in diseases:
                disease_id = disease.get("disease_id")
                patient_count = sum(1 for r in relations if r.get("diagnosed_disease_id") == disease_id)
                disease_patient_counts.append({
                    "disease_id": disease_id,
                    "disease_name": disease.get("disease_name"),
                    "patient_count": patient_count
                })
        except Exception as e:
            return {"message": "Failed to calculate disease patient counts", "error": str(e), "function": "get_disease_patient_counts"}

        return {"message": "Disease patient counts retrieved successfully", "disease_patient_counts": disease_patient_counts, "function": "get_disease_patient_counts"}


    async def get_disease_patient_counts(self):
        try:
            diseases = await self.db.get_all_documents("diseases")
        except Exception as e:
            return {"message": "Failed to retrieve diseases", "error": str(e), "function": "get_disease_patient_counts"}

        try:
            relations = await self.db.get_all_documents("doctor_patient_relations")
        except Exception as e:
            return {"message": "Failed to retrieve doctor-patient relations", "error": str(e), "function": "get_disease_patient_counts"}

        disease_patient_counts = []
        try:
            for disease in diseases:
                disease_id = disease.get("disease_id")
                patient_count = sum(1 for r in relations if r.get("diagnosed_disease_id") == disease_id and r.get("treatment_status") == "Ongoing")
                disease_patient_counts.append({
                    "disease_id": disease_id,
                    "disease_name": disease.get("disease_name"),
                    "patient_count": patient_count
                })
        except Exception as e:
            return {"message": "Failed to calculate disease patient counts", "error": str(e), "function": "get_disease_patient_counts"}

        return {"message": "Disease patient counts retrieved successfully", "disease_patient_counts": disease_patient_counts, "function": "get_disease_patient_counts"}
