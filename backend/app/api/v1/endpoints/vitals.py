from fastapi import APIRouter, HTTPException, Depends
from app.models.schema import ClinicalFeatureVector, WellnessAssessmentOutput
from app.brain.agents import cardio_brain
from app.services.db_service import db_service
from app.services.whatsapp_service import whatsapp_service
from typing import List, Dict, Any
import asyncio

router = APIRouter()

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_history(patient_id: str = "patient_001"):
    """
    Retrieves history for the current patient.
    """
    try:
        history = await db_service.get_patient_history(patient_id)
        return history
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Error fetching clinical history")

@router.post("/ingest", response_model=WellnessAssessmentOutput)
async def ingest_vitals(feature_vector: ClinicalFeatureVector):
    """
    RECEIVES vitals from Patient PWA for Wellness Tracking.
    STORES raw data in Firestore.
    ACTIVATES Wellness Analytics Engine.
    RETURNS assessment (Neural Vector + Suggestion).
    """
    try:
        # 1. Store Raw Vitals
        patient_id = "patient_001" 
        
        vitals_data = feature_vector.current_vitals.copy()
        vitals_data['meta_age'] = feature_vector.age
        vitals_data['meta_bmi'] = feature_vector.bmi
        
        await db_service.add_vital_reading(patient_id, vitals_data)

        # 2. Wellness Analysis (The "Brain") - Multi-agent Orchestration
        assessment = cardio_brain.process_vitals_loop(feature_vector)
        
        # 3. Store Assessment Result (The "Memory")
        assessment_record = assessment.model_dump()
        assessment_record['patient_id'] = patient_id
        
        await db_service.save_assessment(assessment_record)

        # 4. Hrdai-Pro Live Broadcasts (WhatsApp/Emergency Integration)
        user_name = feature_vector.history_flags.get("user_display_name", "Arjun Sharma")
        
        if assessment.significant_deviation_detected:
            # 🚨 Trigger Emergency Response BROADCAST
            asyncio.create_task(whatsapp_service.trigger_emergency_alert(
                user_name=user_name,
                vitals=vitals_data,
                deviation_score=assessment.neural_assessment_vector
            ))
            print(f"🚨 Hridai: EMERGENCY Broadcast sent for {user_name}!")
        else:
            # 📡 Regular Wellness Update Broadcast
            asyncio.create_task(whatsapp_service.send_broadcast(
                user_name=user_name,
                wellness_index=assessment.neural_assessment_vector,
                location=feature_vector.history_flags.get("location", "New Delhi")
            ))
            print(f"📡 Hridai: Wellness Broadcast sent for {user_name}.")

        return assessment

    except Exception as e:
        print(f"Error processing vitals: {e}")
        raise HTTPException(status_code=500, detail="Internal Brain Error during processing")
