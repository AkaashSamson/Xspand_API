from app.database.firebase import FirebaseDB
from app.models.schemas import XRayScan
from fastapi import HTTPException
from datetime import datetime
from typing import List, Dict
from firebase_admin import firestore
from app.imageurl_classify import ImageClassifier
from app.models.enums import TreatmentStatus

model = ImageClassifier()

class XRayService:
    def __init__(self, db: FirebaseDB):
        self.db = db

    async def add_xray_scan(self, scan: XRayScan) -> dict:
        """
        Add a new X-ray scan and use Firebase's generated document ID as scan_id
        """
        try:
            # Convert scan to dict, excluding scan_id since it will be None
            scan_dict = scan.dict(exclude={'scan_id'})
            
            # Set timestamp if not provided
            if not scan_dict.get('scan_timestamp'):
                scan_dict['scan_timestamp'] = datetime.now().isoformat()
            
            # Create a new document reference with auto-generated ID
            doc_ref = self.db.db.collection("xray_scans").document()
            
            # Get the auto-generated ID
            doc_id = doc_ref.id
            
            # Add the ID to our data
            scan_dict['scan_id'] = doc_id
            
            # Create the document with the data
            doc_ref.set(scan_dict)
            
            return {
                "message": "X-ray scan added successfully",
                "scan_id": doc_id,
                "scan_details": scan_dict
            }
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error adding X-ray scan: {str(e)}"
            )

    async def add_xray_scan_classify(self, scan: XRayScan) -> dict:
        """
        Add a new X-ray scan and use Firebase's generated document ID as scan_id
        """
        try:
            # Convert scan to dict, excluding scan_id since it will be None
            scan_dict = scan.dict(exclude={'scan_id'})
            
            # Set timestamp if not provided
            if not scan_dict.get('scan_timestamp'):
                scan_dict['scan_timestamp'] = datetime.now().isoformat()
            
            try:
                model = ImageClassifier()
                scan_dict['ai_classification'] = model.classify(scan_dict['image_url'])
            except Exception as e:
                raise HTTPException(
                status_code=400,
                detail=f"Error classifying X-ray image: {str(e)}"
            )
            # Create a new document reference with auto-generated ID
            doc_ref = self.db.db.collection("xray_scans").document()
            
            # Get the auto-generated ID
            doc_id = doc_ref.id
            
            # Add the ID to our data
            scan_dict['scan_id'] = doc_id
            
            # Create the document with the data
            doc_ref.set(scan_dict)
            
            return {
                "message": "X-ray scan added successfully",
                "scan_id": doc_id,
                "scan_details": scan_dict
            }
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error adding X-ray scan: {str(e)}"
            )


    async def update_xray_scan(self, scan_id: str, update_data: Dict) -> dict:
        """
        Update any fields in the X-ray scan document
        """
        try:
            if update_data.get('ai_approved'):
                update_data['no_findings_detected'] = False
                update_data['disease_name'] = update_data['ai_classification']
                # Get disease id where disease name is matched
                try:
                    disease_query = self.db.db.collection("diseases").where("disease_name", "==", update_data['disease_name']).stream()
                    disease = None
                    for doc in disease_query:
                        disease = doc.to_dict()
                        break
                    if not disease:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Disease with name {update_data['disease_name']} not found"
                        )
                    update_data['disease_id'] = disease['disease_id']
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error fetching disease document: {str(e)}"
                    )

            # Get the ongoing doctor_patient relationship
            try:
                current_scan = await self.db.get_document("xray_scans", scan_id)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error fetching current X-ray scan document: {str(e)}"
                )

            doc_id = f"{current_scan['doctor_id']}_{current_scan['patient_id']}"
            try:
                doc = await self.db.get_document("doctor_patient_relations", doc_id)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error fetching doctor-patient relationship document: {str(e)}"
                )

            if doc and doc.get('treatment_status') == TreatmentStatus.ongoing:
                try:
                    await self.db.update_document("doctor_patient_relations", doc_id, {'diagnosed_disease_id': update_data['disease_id'], 'diagnosed_with_disease': True})
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error updating doctor-patient relationship document: {str(e)}"
                    )

            # Update the X-ray scan document
            try:
                await self.db.update_document("xray_scans", scan_id, update_data)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error updating X-ray scan document: {str(e)}"
                )

            # Get and return the updated document
            try:
                updated_scan = await self.db.get_document("xray_scans", scan_id)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error fetching updated X-ray scan document: {str(e)}"
                )

            return {
                "message": "X-ray scan updated successfully",
                "scan_id": scan_id,
                "scan_details": updated_scan
            }

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error updating X-ray scan: {str(e)}"
            )
    async def get_all_xrays(self) -> List[dict]:
        """
        Get all X-ray scans
        """
        try:
            scans = await self.db.get_all_documents("xray_scans")
            return scans
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error fetching X-ray scans: {str(e)}"
            )

    async def get_unverified_xrays(self) -> List[dict]:
        """
        Get all X-ray scans that haven't been verified by a radiologist (radiologist_id is null)
        """
        try:
            all_scans = await self.db.get_all_documents("xray_scans")
            unverified_scans = [
                scan for scan in all_scans 
                if scan.get("radiologist_id") is None
            ]
            return unverified_scans
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error fetching unverified X-ray scans: {str(e)}"
            )
    
    async def classify_xray(self, scan_id: str) -> str:
        """
        Classify an X-ray scan based on its AI classification
        """
        try:
            scan = await self.db.get_document("xray_scans", scan_id)
            if not scan:
                raise HTTPException(
                    status_code=404,
                    detail=f"X-ray scan {scan_id} not found"
                )

            model = ImageClassifier()
            return model.classify(scan.get("image_url"))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error classifying X-ray scan: {str(e)}"
            )

    
    async def classify_image_url(self, image_url: str) -> str:
        """
        Classify an X-ray image directly from an image URL
        """
        try:
            model = ImageClassifier()
            return model.classify(image_url)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error classifying X-ray image: {str(e)}"
            )

    
    async def get_xrays_by_patient_id(self, patient_id: str) -> List[dict]:
        """
        Get all X-ray scans for a given patient_id
        """
        try:
            all_scans = await self.db.get_all_documents("xray_scans")
            scans_by_patient = [
                scan for scan in all_scans 
                if scan.get("patient_id") == patient_id
            ]
            return scans_by_patient
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error fetching X-ray scans for patient {patient_id}: {str(e)}"
            )

    async def delete_xray_scan(self, xray_scan_id: str) -> dict:
        """
        Delete an X-ray scan based on its ID
        """
        try:
            await self.db.delete_document("xray_scans", xray_scan_id)
            return {
                "message": "X-ray scan deleted successfully",
                "xray_scan_id": xray_scan_id
            }
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error deleting X-ray scan: {str(e)}"
            )


    