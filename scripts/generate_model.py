import xgboost as xgb
import numpy as np
import pickle
import os

# 22 Features as defined in antigravity_main.py
FEATURES = [
    "age", "sex", "cholesterol", "blood_pressure", "heart_rate", "diabetes",
    "family_history", "smoking", "obesity", "alcohol_consumption",
    "exercise_hours_per_week", "diet", "previous_heart_problems",
    "medication_use", "stress_level", "sedentary_hours_per_day", "bmi",
    "triglycerides", "physical_activity_days_per_week", "sleep_hours_per_day",
    "chest_pain", "blood_sugar"
]

# Create dummy training data
X = np.random.rand(100, 22)
y = np.random.randint(0, 2, 100)

model = xgb.XGBClassifier()
model.fit(X, y)

# Set feature names (very important for SHAP and XGBoost in v4 code)
model.get_booster().feature_names = FEATURES

os.makedirs('/Users/home/Desktop/CardioGuard AI/v4/model', exist_ok=True)
with open('/Users/home/Desktop/CardioGuard AI/v4/model/antigravity_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Generated dummy 22-feature XGBoost model.")
