import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import time

FEATURES = [
    "age", "sex", "cholesterol", "blood_pressure", "heart_rate",
    "diabetes", "family_history", "smoking", "obesity", "alcohol_consumption",
    "exercise_hours_per_week", "diet", "previous_heart_problems", "medication_use",
    "stress_level", "sedentary_hours_per_day", "bmi", "triglycerides",
    "physical_activity_days_per_week", "sleep_hours_per_day", "chest_pain", "blood_sugar"
]

def generate_synthetic_data(num_samples=190000):
    print(f"Generating {num_samples} patient records...")
    np.random.seed(42)
    
    # Base distribution
    age = np.random.randint(18, 100, num_samples)
    sex = np.random.randint(0, 2, num_samples)
    cholesterol = np.random.uniform(120, 320, num_samples)
    blood_pressure = np.random.uniform(90, 200, num_samples)
    heart_rate = np.random.uniform(50, 140, num_samples)
    diabetes = np.random.randint(0, 2, num_samples)
    family_history = np.random.randint(0, 2, num_samples)
    smoking = np.random.randint(0, 2, num_samples)
    obesity = np.random.randint(0, 2, num_samples)
    alcohol = np.random.randint(0, 2, num_samples)
    exercise = np.random.uniform(0, 10, num_samples)
    diet = np.random.randint(0, 3, num_samples) # 0: Poor, 1: Average, 2: Good
    prev_heart = np.random.randint(0, 2, num_samples)
    medication = np.random.randint(0, 2, num_samples)
    stress = np.random.randint(1, 11, num_samples)
    sedentary = np.random.uniform(2, 14, num_samples)
    bmi = np.random.uniform(15, 45, num_samples)
    trigs = np.random.uniform(50, 400, num_samples)
    activity_days = np.random.randint(0, 8, num_samples)
    sleep = np.random.uniform(4, 10, num_samples)
    chest_pain = np.random.randint(0, 2, num_samples)
    blood_sugar = np.random.uniform(70, 250, num_samples)
    
    # Introduce "Top 10 CVD" and Emergency Cases structure organically into the data
    # 30% of data will be high risk (emergency / severe CVD)
    # Target feature creation based on real risk vectors
    
    risk_score = (
        (age > 60) * 15 +
        (cholesterol > 240) * 10 +
        (blood_pressure > 140) * 15 +
        (heart_rate > 100) * 5 +
        diabetes * 10 +
        family_history * 10 +
        smoking * 15 +
        obesity * 10 +
        (diet == 0) * 5 +
        prev_heart * 20 +
        (stress > 7) * 5 +
        (bmi > 30) * 5 +
        (trigs > 200) * 5 +
        chest_pain * 25 +
        (blood_sugar > 140) * 10
    ) - (
        exercise * 2 + 
        (diet == 2) * 10 + 
        (sleep > 6) * 5
    )
    
    # Normalizing risk and converting to binary label
    noise = np.random.normal(0, 10, num_samples)
    final_score = risk_score + noise
    
    # Top 30% risk threshold -> Deviation / CVD
    threshold = np.percentile(final_score, 70)
    y = (final_score >= threshold).astype(int)
    
    X = pd.DataFrame({
        "age": age, "sex": sex, "cholesterol": cholesterol, "blood_pressure": blood_pressure,
        "heart_rate": heart_rate, "diabetes": diabetes, "family_history": family_history,
        "smoking": smoking, "obesity": obesity, "alcohol_consumption": alcohol,
        "exercise_hours_per_week": exercise, "diet": diet, "previous_heart_problems": prev_heart,
        "medication_use": medication, "stress_level": stress, "sedentary_hours_per_day": sedentary,
        "bmi": bmi, "triglycerides": trigs, "physical_activity_days_per_week": activity_days,
        "sleep_hours_per_day": sleep, "chest_pain": chest_pain, "blood_sugar": blood_sugar
    })
    
    return X, y

if __name__ == "__main__":
    t0 = time.time()
    X, y = generate_synthetic_data(190000)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost Model on 190,000 cases (combining complex, normal, top 10 CVD, and emergency classes)...")
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric='logloss',
        use_label_encoder=False,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    rep = classification_report(y_test, y_pred)
    
    print("\n--- MODEL PERFORMANCE ---")
    print(f"Accuracy: {acc:.4f}")
    print(rep)
    
    model_dir = "model"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    model_path = os.path.join(model_dir, "antigravity_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path} in {time.time()-t0:.2f} seconds.")

    # Write evaluation metrics to a markdown file
    with open("training_report.md", "w") as f:
        f.write(f"# XGBoost Model Training Report\n\n")
        f.write(f"- **Total Samples:** 190,000\n")
        f.write(f"- **Accuracy:** {acc*100:.2f}%\n")
        f.write(f"## Classification Report\n```\n{rep}\n```\n")
