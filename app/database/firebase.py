from firebase_admin import firestore, auth
from fastapi import HTTPException

class FirebaseDB:
    def __init__(self):
        self.db = firestore.client()

    async def create_user_auth(self, email: str, password: str) -> str:
        try:
            user_record = auth.create_user(
                email=email,
                password=password
            )
            return user_record.uid
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_user_auth(self, user_id: str):
        try:
            auth.delete_user(user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def create_document(self, collection: str, doc_id: str, data: dict):
        try:
            self.db.collection(collection).document(doc_id).set(data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_document(self, collection: str, doc_id: str, data: dict):
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            current_data = doc_ref.get().to_dict()
            if not current_data:
                raise HTTPException(status_code=404, detail=f"Document not found in {collection}")
            current_data.update(data)
            doc_ref.set(current_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_document(self, collection: str, doc_id: str):
        try:
            self.db.collection(collection).document(doc_id).delete()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_all_documents(self, collection: str) -> list:
        try:
            docs = self.db.collection(collection).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_document(self, collection: str, doc_id: str) -> dict:
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail=f"Document not found in {collection}")
            return doc.to_dict()
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_doctor_patient_relations(self, patient_id: str) -> list:
        try:
            # Get all documents from doctor_patient_relations collection
            docs = self.db.collection("doctor_patient_relations").stream()
            # Filter for the specific patient_id
            relations = []
            for doc in docs:
                data = doc.to_dict()
                if data.get("patient_id") == patient_id:
                    data["relation_id"] = doc.id  # Add the document ID
                    relations.append(data)
            return relations
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
