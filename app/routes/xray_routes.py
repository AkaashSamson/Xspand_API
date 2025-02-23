from fastapi import APIRouter, Depends
from app.services.xray_service import XRayService
from app.models.schemas import XRayScan
from app.database.firebase import FirebaseDB
from typing import List, Dict

router = APIRouter(
    tags=["X-Ray Scans"]
)

def get_xray_service():
    db = FirebaseDB()
    return XRayService(db)

@router.post("/")
async def add_xray_scan(
    scan: XRayScan,
    service: XRayService = Depends(get_xray_service)
):
    """
    Add a new X-ray scan. The scan_id will be automatically generated by Firebase.
    """
    return await service.add_xray_scan(scan)

@router.post("/classify")
async def add_xray_scan_classify(
    scan: XRayScan,
    service: XRayService = Depends(get_xray_service)
):
    """
    Add a new X-ray scan and classify it. The scan_id will be automatically generated by Firebase.
    """
    return await service.add_xray_scan_classify(scan)

@router.put("/{scan_id}")
async def update_xray_scan(
    scan_id: str,
    update_data: Dict,
    service: XRayService = Depends(get_xray_service)
):
    """
    Update any fields in an existing X-ray scan
    """
    return await service.update_xray_scan(scan_id, update_data)

@router.get("/")
async def get_all_xrays(
    service: XRayService = Depends(get_xray_service)
) -> List[dict]:
    """
    Get all X-ray scans
    """
    return await service.get_all_xrays()

@router.get("/unverified")
async def get_unverified_xrays(
    service: XRayService = Depends(get_xray_service)
) -> List[dict]:
    """
    Get all X-ray scans that haven't been verified by a radiologist yet
    """
    return await service.get_unverified_xrays()

@router.get("/classify/{scan_id}")
async def classify_xray(
    scan_id: str,
    service: XRayService = Depends(get_xray_service)
) -> str:
    """
    Classify an X-ray scan based on its AI classification
    """
    return await service.classify_xray(scan_id)

@router.get("/classify_url/")
async def classify_image_url(
    image_url: str,
    service: XRayService = Depends(get_xray_service)
) -> str:
    """
    Classify an X-ray image directly from an image URL
    """
    return await service.classify_image_url(image_url)


@router.get("/by_patient/{patient_id}")
async def get_xrays_by_patient_id(
    patient_id: str,
    service: XRayService = Depends(get_xray_service)
) -> List[dict]:
    """
    Get all X-ray scans for a given patient_id
    """
    return await service.get_xrays_by_patient_id(patient_id)

@router.delete("/delete/{scan_id}")
async def delete_xray_scan(
    scan_id: str,
    service: XRayService = Depends(get_xray_service)
) -> dict:
    """
    Delete an X-ray scan based on its ID
    """
    return await service.delete_xray_scan(scan_id)