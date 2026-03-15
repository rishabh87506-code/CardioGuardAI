from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime

# --- Input Models (Synapses In) ---

class ClinicalFeatureVector(BaseModel):
    """Standardized input vector for the 10-disease loop."""
    age: int = Field(..., description="Patient age in years")
    sex: Literal['M', 'F', 'O'] = Field(..., description="Biological sex")
    bmi: float = Field(..., description="Body Mass Index")
    current_vitals: Dict[str, float] = Field(..., description="Map of vitals e.g. {'hr': 72, 'sbp': 120}")
    symptoms: List[str] = Field(default_factory=list, description="List of reported symptoms")
    history_flags: Dict[str, bool] = Field(default_factory=dict, description="Medical history flags e.g. {'diabetes': True}")

# --- Output Models (Synapses Out) ---

class PatternObservation(BaseModel):
    """Observation of a specific physiological pattern."""
    pattern_name: str
    assessment_index: float = Field(..., ge=0.0, le=1.0)
    confidence_interval: tuple[float, float]
    observation_level: Literal['baseline', 'moderate_deviation', 'significant_deviation', 'urgent_evaluation']
    contributing_factors: List[str]

class WellnessAssessmentOutput(BaseModel):
    """Final Wellness Assessment for use in lifestyle monitoring."""
    timestamp: datetime = Field(default_factory=datetime.now)
    neural_assessment_vector: int = Field(..., ge=0, le=100)
    significant_observations: List[PatternObservation]
    wellness_suggestion: str
    significant_deviation_detected: bool = False
    nearest_healthcare_resource: Optional[Dict] = None

# --- Firestore Document Models (Storage) ---

class PatientProfile(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    medical_history: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)

class VitalReading(BaseModel):
    id: Optional[str] = None
    patient_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    type: str # "heart_rate", "bp", etc.
    value: float | dict 
    source: str = "manual"
