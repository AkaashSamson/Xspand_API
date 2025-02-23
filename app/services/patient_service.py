from app.database.firebase import FirebaseDB
from app.models.schemas import (
    Patient, PatientRegistration, DoctorPatientRelation, 
    XRayScan, SimplePatientRegistration, CompletePatientRegistration
)
from app.models.enums import TreatmentStatus
from fastapi import HTTPException
from datetime import datetime
from typing import Optional

class PatientService:
    def __init__(self, db: FirebaseDB):
        self.db = db

    async def add_new_patient(self, registration: SimplePatientRegistration):
        try:
            # Check if patient already exists
            patient_exists = True
            try:
                await self.db.get_document("patients", registration.patient_id)
            except HTTPException as e:
                if e.status_code == 404:  # Not found error
                    patient_exists = False
                else:  # Any other HTTP error
                    raise e

            # If patient doesn't exist, create new patient with minimal info
            if not patient_exists:
                patient_data = {
                    "patient_id": registration.patient_id,
                    "is_resident": registration.is_resident
                }
                await self.db.create_document("patients", registration.patient_id, patient_data)

            # Check if there's an existing ongoing relationship
            relation_id = f"{registration.doctor_id}_{registration.patient_id}"
            try:
                existing_relation = await self.db.get_document("doctor_patient_relations", relation_id)
                if existing_relation and existing_relation.get("treatment_status") == TreatmentStatus.ongoing:
                    return {
                        "message": "An ongoing doctor-patient relationship already exists",
                        "patient_id": registration.patient_id,
                        "relation_id": relation_id,
                        "treatment_status": existing_relation.get("treatment_status"),
                        "treatment_start_date": existing_relation.get("treatment_start_date")
                    }
            except HTTPException as e:
                if e.status_code != 404:  # If error is not "not found"
                    raise e

            # Create new doctor-patient relationship
            relation = DoctorPatientRelation(
                doctor_id=registration.doctor_id,
                patient_id=registration.patient_id,
                treatment_status=TreatmentStatus.ongoing,
                treatment_start_date=datetime.now().isoformat(),
                treatment_end_date=None,
                diagnosed_with_disease=False,
                diagnosed_disease_id=None
            )
            
            await self.db.create_document("doctor_patient_relations", relation_id, relation.dict())

            if patient_exists:
                return {
                    "message": "Patient already exists, created new doctor-patient relationship",
                    "patient_id": registration.patient_id,
                    "relation_id": relation_id
                }
            else:
                return {
                    "message": "New patient registered successfully with doctor relationship",
                    "patient_id": registration.patient_id,
                    "relation_id": relation_id
                }

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=400,
                detail=f"Error registering patient: {str(e)}"
            )

    async def register_complete_patient(self, registration: CompletePatientRegistration):
        try:
            # Check if patient already exists
            try:
                await self.db.get_document("patients", registration.patient_id)
                return {
                    "message": "Patient ID already exists",
                    "patient_id": registration.patient_id
                }
            except HTTPException as e:
                if e.status_code != 404:  # If error is not "not found"
                    raise e

            # Check if there's an existing ongoing relationship
            relation_id = f"{registration.doctor_id}_{registration.patient_id}"
            try:
                existing_relation = await self.db.get_document("doctor_patient_relations", relation_id)
                if existing_relation and existing_relation.get("treatment_status") == TreatmentStatus.ongoing:
                    return {
                        "message": "An ongoing doctor-patient relationship already exists",
                        "patient_id": registration.patient_id,
                        "relation_id": relation_id,
                        "treatment_status": existing_relation.get("treatment_status"),
                        "treatment_start_date": existing_relation.get("treatment_start_date")
                    }
            except HTTPException as e:
                if e.status_code != 404:  # If error is not "not found"
                    raise e

            # Create patient with all details
            patient_data = {
                "patient_id": registration.patient_id,
                "full_name": registration.full_name,
                "is_resident": registration.is_resident,
                "email_address": registration.email_address,
                "contact_number": registration.contact_number,
                "age": registration.age,
                "height_cm": registration.height_cm,
                "weight_kg": registration.weight_kg,
                "gender": registration.gender
            }
            await self.db.create_document("patients", registration.patient_id, patient_data)

            # Create doctor-patient relationship
            relation = DoctorPatientRelation(
                doctor_id=registration.doctor_id,
                patient_id=registration.patient_id,
                treatment_status=TreatmentStatus.ongoing,
                treatment_start_date=datetime.now().isoformat(),
                treatment_end_date=None,
                diagnosed_with_disease=False,
                diagnosed_disease_id=None
            )
            
            await self.db.create_document("doctor_patient_relations", relation_id, relation.dict())

            return {
                "message": "Patient registered successfully with doctor relationship",
                "patient_id": registration.patient_id,
                "relation_id": relation_id,
                "patient_details": patient_data
            }

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=400,
                detail=f"Error registering patient with details: {str(e)}"
            )

    async def update_patient(self, patient_id: str, patient: dict):
        
        try:
            # Check if patient exists
            try:
                await self.db.get_document("patients", patient_id)
            except HTTPException as e:
                if e.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Patient with ID {patient_id} not found"
                    )
                else:
                    raise e

            # Update patient
            await self.db.update_document("patients", patient_id, patient)
            return {"message": "Patient updated successfully"}
        except Exception as e:
            if isinstance(e, HTTPException):
              raise e
            raise HTTPException(
            status_code=400,
            detail=f"Error updating patient: {str(e)}"
            )

    async def delete_patient(self, patient_id: str):
        # Get all relations for this patient
        relations = await self.db.get_all_documents("doctor_patient_relations")
        for relation in relations:
            if relation.get("patient_id") == patient_id:
                relation_id = f"{relation['doctor_id']}_{patient_id}"
                await self.db.delete_document("doctor_patient_relations", relation_id)
        
        # Delete patient
        await self.db.delete_document("patients", patient_id)
        return {"message": "Patient and related records deleted successfully"}

    async def get_patient(self, patient_id: str):
        patient = await self.db.get_document("patients", patient_id)
        return {"message": "Patient retrieved successfully", "patient": patient}

    async def get_all_patients(self):
        patients = await self.db.get_all_documents("patients")
        return {"message": "Patients retrieved successfully", "patients": patients}

    async def get_doctor_patients(self, doctor_id: str):
        relations = await self.db.get_all_documents("doctor_patient_relations")
        doctor_relations = [r for r in relations if r.get("doctor_id") == doctor_id]
        
        patients = []
        for relation in doctor_relations:
            patient = await self.db.get_document("patients", relation["patient_id"])
            if patient:
                patients.append({
                    "patient": patient,
                    "treatment_status": relation["treatment_status"],
                    "treatment_start_date": relation["treatment_start_date"],
                    "treatment_end_date": relation["treatment_end_date"]
                })
        
        return {
            "message": "Doctor's patients retrieved successfully",
            "patients": patients
        }

    async def add_xray_scan(self, scan: XRayScan):
        await self.db.create_document("xray_scans", scan.scan_id, scan.dict())
        return {"message": "X-ray scan added successfully", "scan_id": scan.scan_id}

    async def get_patient_scans(self, patient_id: str):
        scans = await self.db.get_all_documents("xray_scans")
        patient_scans = [scan for scan in scans if scan.get("patient_id") == patient_id]
        return {
            "message": "Patient scans retrieved successfully",
            "scans": patient_scans
        }

    async def update_treatment_status(self, doctor_id: str, patient_id: str, status: TreatmentStatus, disease_id: Optional[str] = None):
        try:
            relation_id = f"{doctor_id}_{patient_id}"
            
            # Get current treatment data
            current_treatment = await self.db.get_document("doctor_patient_relations", relation_id)
            if not current_treatment:
                raise HTTPException(
                    status_code=404,
                    detail=f"Treatment relation not found for doctor {doctor_id} and patient {patient_id}"
                )

            # Prepare update data
            update_data = {
                "treatment_status": status,
            }

            # Handle end_date based on status
            if status == TreatmentStatus.completed:
                update_data["treatment_end_date"] = datetime.now().isoformat()
            elif status == TreatmentStatus.ongoing:
                update_data["treatment_end_date"] = None

            # Update disease information if provided
            if disease_id:
                update_data.update({
                    "diagnosed_with_disease": True,
                    "diagnosed_disease_id": disease_id
                })
            
            await self.db.update_document("doctor_patient_relations", relation_id, update_data)
            
            # Get updated treatment for response
            updated_treatment = await self.db.get_document("doctor_patient_relations", relation_id)
            return {
                "message": "Treatment status updated successfully",
                "treatment_details": updated_treatment
            }

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=400,
                detail=f"Error updating treatment status: {str(e)}"
            )

    async def update_treatment(self, patient_id: str, doctor_id: str, treatment_data: dict):
        try:
            # Get all doctor-patient relations for this patient
            relations = await self.db.get_all_documents("doctor_patient_relations")
            relations = [relation for relation in relations if relation.get("patient_id") == patient_id]
            if not relations:
                raise HTTPException(
                    status_code=404,
                    detail=f"No treatment records found for patient {patient_id}"
                )

            # First, look for an ongoing treatment (end_date is None)
            ongoing_relation = None
            latest_completed_relation = None
            latest_end_date = None

            for relation in relations:
                if relation.get("doctor_id") != doctor_id:
                    continue

                if relation.get("treatment_end_date") is None:
                    ongoing_relation = relation
                    break
                else:
                    # Convert string date to datetime for comparison
                    end_date = datetime.fromisoformat(relation.get("treatment_end_date"))
                    if latest_end_date is None or end_date > latest_end_date:
                        latest_end_date = end_date
                        latest_completed_relation = relation

            # Determine which relation to update
            relation_to_update = ongoing_relation if ongoing_relation else latest_completed_relation

            if not relation_to_update:
                raise HTTPException(
                    status_code=404,
                    detail=f"No treatment record found for patient {patient_id} with doctor {doctor_id}"
                )

            # Update the treatment
            relation_id = f"{relation_to_update['doctor_id']}_{relation_to_update['patient_id']}"
            await self.db.update_document("doctor_patient_relations", relation_id, treatment_data)

            # Get and return the updated record
            updated_relation = await self.db.get_document("doctor_patient_relations", relation_id)
            return {
                "message": "Treatment updated successfully",
                "relation_id": relation_id,
                "treatment_details": updated_relation
            }

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=400,
                detail=f"Error updating treatment: {str(e)}"
            )

    async def get_patient_complete_details(self, patient_id: str):
        try:
            # Get patient details
            patient_details = await self.db.get_document("patients", patient_id)
            if not patient_details:
                raise HTTPException(
                    status_code=404,
                    detail=f"Patient {patient_id} not found"
                )

            # Get all doctor-patient relations for this patient
            relations = await self.db.get_doctor_patient_relations(patient_id)
            
            # Find the ongoing treatment
            ongoing_treatment = None
            for relation in relations:
                if relation.get("treatment_end_date") is None:
                    ongoing_treatment = relation
                    break

            if not ongoing_treatment:
                # Return patient details without treatment info if no ongoing treatment
                return {
                    "patient_details": patient_details,
                    "message": "No ongoing treatment found"
                }

            # Get doctor details
            doctor_id = ongoing_treatment.get("doctor_id")
            try:
                doctor_details = await self.db.get_document("doctors", doctor_id)
            except HTTPException as e:
                doctor_details = {"message": f"Doctor details not found: {str(e)}"}

            # Get disease details if exists
            disease_details = None
            if ongoing_treatment.get("diagnosed_with_disease") and ongoing_treatment.get("diagnosed_disease_id"):
                try:
                    disease_details = await self.db.get_document(
                        "diseases", 
                        ongoing_treatment.get("diagnosed_disease_id")
                    )
                except HTTPException as e:
                    disease_details = {"message": f"Disease details not found: {str(e)}"}

            # Construct the response
            response = {
                "patient_details": patient_details,
                "current_treatment": {
                    "doctor_details": doctor_details,
                    "treatment_status": ongoing_treatment.get("treatment_status"),
                    "treatment_start_date": ongoing_treatment.get("treatment_start_date"),
                }
            }

            # Add disease details if they exist
            if disease_details:
                response["current_treatment"]["disease_details"] = disease_details

            return response

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=400,
                detail=f"Error fetching patient details: {str(e)}"
            )
