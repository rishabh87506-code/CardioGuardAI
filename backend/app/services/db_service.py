import firebase_admin
from firebase_admin import credentials, firestore
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

# Initialize Firebase Admin
# In production, this uses Application Default Credentials automatically.
# For local dev, you might need to set GOOGLE_APPLICATION_CREDENTIALS env var.

try:
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': os.getenv('GOOGLE_CLOUD_PROJECT', 'cardioguard-ai'),
        })
    db = firestore.client()
    print("Firestore connected.")
except Exception as e:
    print(f"Warning: Firestore could not be initialized. Running in Mock Mode. Error: {e}")
    db = None

class DatabaseService:
    def __init__(self):
        self.db = db

    async def add_vital_reading(self, patient_id: str, data: Dict[str, Any]) -> str:
        """Adds a new vital reading to the 'vitals' collection."""
        if not self.db:
            print(f"[MOCK DB] Added vital for {patient_id}: {data}")
            return "mock-vital-id-123"
        
        doc_ref = self.db.collection('vitals').document()
        # Ensure timestamp is set
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now()
        
        data['patient_id'] = patient_id
        doc_ref.set(data)
        return doc_ref.id

    async def get_patient_history(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves recent vitals for a patient."""
        if not self.db:
            return [{"mock_data": True, "value": 80, "type": "heart_rate"}]

        vitals_ref = self.db.collection('vitals')
        query = vitals_ref.where('patient_id', '==', patient_id)\
                          .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                          .limit(limit)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    async def save_assessment(self, assessment_data: Dict[str, Any]) -> str:
        """Saves a risk assessment result."""
        if not self.db:
             print(f"[MOCK DB] Saved assessment: {assessment_data}")
             return "mock-assessment-id-456"
        
        doc_ref = self.db.collection('assessments').document()
        doc_ref.set(assessment_data)
        return doc_ref.id

db_service = DatabaseService()
