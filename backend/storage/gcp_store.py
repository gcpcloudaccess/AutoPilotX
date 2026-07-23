"""
GCP integration module for future use.
Placeholder for Cloud Firestore and Container Registry integration.
"""

from typing import List, Optional
from models import ScanResult

class FirestoreStorage:
    """Store scan results in Cloud Firestore"""

    def __init__(self, project_id: str):
        # from google.cloud import firestore
        # self.db = firestore.Client(project=project_id)
        pass

    def save_scan(self, result: ScanResult) -> str:
        """Save scan result to Firestore"""
        # self.db.collection('scans').add(result.to_dict())
        raise NotImplementedError("Connect to GCP first")

    def get_scan(self, scan_id: str) -> Optional[dict]:
        """Retrieve scan from Firestore"""
        raise NotImplementedError("Connect to GCP first")

    def list_scans(self, image: str = None, limit: int = 10) -> List[dict]:
        """List recent scans"""
        raise NotImplementedError("Connect to GCP first")


class GCRClient:
    """Interact with Google Container Registry"""

    def __init__(self, project_id: str):
        # from google.cloud import container_v1
        # self.client = container_v1.ContainerClient()
        self.project_id = project_id

    def list_images(self) -> List[str]:
        """List all images in GCR"""
        raise NotImplementedError("Connect to GCP first")

    def get_image_layers(self, image: str) -> dict:
        """Get image layer information"""
        raise NotImplementedError("Connect to GCP first")
