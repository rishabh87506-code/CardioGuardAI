import joblib
import os
import pandas as pd
import numpy as np
from datetime import datetime
from app.models.schema import ClinicalFeatureVector, WellnessAssessmentOutput, PatternObservation

class WellnessAnalyticsEngine:
    def __init__(self):
        # Load the trained extraordinary model
        model_path = os.path.join(os.path.dirname(__file__), 'cvd_model.pkl')
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.model_available = True
        else:
            self.model_available = False

    def assess_wellness_vector(self, vector: ClinicalFeatureVector) -> WellnessAssessmentOutput:
        """
        Analyzes the ClinicalFeatureVector using the calibrated Random Forest model for wellness monitoring.
        """
        
        # 1. Prepare Features for the model
        sex_map = {'M': 1, 'F': 0, 'O': 0}
        
        features = pd.DataFrame([{
            'age': vector.age,
            'sex': sex_map.get(vector.sex, 0),
            'bmi': vector.bmi,
            'hr': vector.current_vitals.get('hr', 70),
            'sbp': vector.current_vitals.get('sbp', 120),
            'dbp': vector.current_vitals.get('dbp', 80),
            'chest_pain': 1 if 'chest_pain' in vector.symptoms else 0,
            'shortness_of_breath': 1 if 'shortness_of_breath' in vector.symptoms else 0
        }])
        
        # 2. Predict Probability (Neural Assessment Index)
        if self.model_available:
            prob = self.model.predict_proba(features)[0][1]
        else:
            prob = 0.5 if features['hr'].iloc[0] > 120 else 0.1
        
        observations = []
        level = "baseline"
        if prob > 0.8: level = "urgent_evaluation"
        elif prob > 0.5: level = "significant_deviation"
        elif prob > 0.2: level = "moderate_deviation"
        
        observations.append(PatternObservation(
            pattern_name="Cardiovascular Wellness Pattern (Neural Assessment)",
            assessment_index=float(prob),
            confidence_interval=(float(prob)-0.05, float(prob)+0.05),
            observation_level=level,
            contributing_factors=self._get_contributing_factors(features)
        ))
        
        # 3. Determine Significant Deviation
        significant_deviation = prob > 0.85 or features['hr'].iloc[0] > 140
        suggestion = "Monitor regularly and maintain healthy lifestyle"
        
        if significant_deviation:
            suggestion = "Significant deviation from personal wellness baseline. We recommend consulting a healthcare professional for a formal medical evaluation."
        elif prob > 0.5:
            suggestion = "Noticeable pattern deviation. Consider scheduling a routine wellness consultation with a healthcare provider."

        return WellnessAssessmentOutput(
            timestamp=datetime.now(),
            neural_assessment_vector=int(prob * 100),
            significant_observations=observations,
            wellness_suggestion=suggestion,
            significant_deviation_detected=significant_deviation,
            nearest_healthcare_resource=None
        )

    def _get_contributing_factors(self, features):
        factors = []
        if features['hr'].iloc[0] > 100: factors.append("elevated_heart_rate")
        if features['sbp'].iloc[0] > 140: factors.append("hypertension")
        if features['chest_pain'].iloc[0] == 1: factors.append("chest_pain_reported")
        return factors

risk_engine = WellnessAnalyticsEngine()
