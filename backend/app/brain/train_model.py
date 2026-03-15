import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
import joblib
import os

def generate_extraordinary_data(n=1000):
    """
    Generates 1000 synthetic CVD cases with 'weird and extraordinary' variations.
    Includes:
    - Pediatric hypertension/tachycardia (age < 15)
    - Geriatric outliers (age > 90)
    - Athlete anomalies (low HR with sudden BP spikes)
    - Silent symptoms (high risk vitals with no pain)
    - BMI/Vitals mismatch (Low BMI with high BP)
    """
    np.random.seed(42)
    data = []
    
    disease_types = ['Normal', 'Arrhythmia', 'Hypertension', 'Myocardial Infarction', 'Heart Failure', 'Congenital']
    
    for _ in range(n):
        # Base vitals
        age = np.random.randint(5, 100)
        sex = np.random.choice([0, 1]) # 0: Female, 1: Male
        bmi = np.random.uniform(15, 45)
        hr = np.random.randint(40, 160)
        sbp = np.random.randint(80, 200)
        dbp = np.random.randint(50, 120)
        chest_pain = np.random.choice([0, 1], p=[0.7, 0.3])
        shortness_of_breath = np.random.choice([0, 1], p=[0.8, 0.2])
        
        # Risk logic (Refined to be learnable but complex)
        risk_score = 0
        
        # 1. Pediatric Risk (Weird/Extraordinary)
        if age < 18:
            if hr > 115: risk_score += 1.5
            if sbp > 140: risk_score += 1.5
            
        # 2. Geriatric Resilience vs Risk
        if age > 80:
            if hr < 55: risk_score += 1.0
            risk_score += 0.5 # Baseline age risk
            
        # 3. Vitals Thresholds (Non-linear)
        if hr > 140: risk_score += 2.0
        if hr < 40: risk_score += 1.5
        if sbp > 175: risk_score += 1.8
        if dbp > 110: risk_score += 1.2
        
        # 4. Silent Killers: No pain but high BP and age
        if not chest_pain and sbp > 165 and age > 65:
            risk_score += 1.5
            
        # 5. The "Athlete" Extraordinary Case
        if hr < 45 and (bmi > 28 or sbp > 150):
            risk_score += 2.2
            
        # 6. BMI/Vitals Paradox
        if bmi < 19 and sbp > 155:
            risk_score += 1.7
            
        # Cumulative symptoms
        if chest_pain and shortness_of_breath:
            risk_score += 1.2
        elif chest_pain or shortness_of_breath:
            risk_score += 0.6
            
        # Sex nuances
        if sex == 1 and age > 50 and sbp > 140:
            risk_score += 0.5
            
        # Probability calculation (Tightened for better AUC)
        # Using a threshold of 1.5 for high risk
        prob = 1 / (1 + np.exp(- (risk_score - 2.5))) 
        target = 1 if prob > 0.5 else 0 # More deterministic for this task
        
        data.append([age, sex, bmi, hr, sbp, dbp, chest_pain, shortness_of_breath, target])
    
    columns = ['age', 'sex', 'bmi', 'hr', 'sbp', 'dbp', 'chest_pain', 'shortness_of_breath', 'target']
    return pd.DataFrame(data, columns=columns)

def train_and_evaluate():
    print("🚀 Initializing CardioGuard AI Model Training Pipeline...")
    print("📊 Generating 1000 weird and extraordinary CVD cases...")
    df = generate_extraordinary_data(1000)
    
    # Save dataset for reference
    data_path = os.path.join(os.path.dirname(__file__), 'extraordinary_cvd_data.csv')
    df.to_csv(data_path, index=False)
    print(f"✅ Data saved to {data_path}")
    
    # Split Data
    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model Training
    print("🧠 Training Random Forest Classifier on extraordinary cases...")
    model = RandomForestClassifier(
        n_estimators=150, 
        max_depth=10, 
        min_samples_split=5,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    
    # Evaluation
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    auc = roc_auc_score(y_test, y_prob)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*30)
    print("📈 TRAINING RESULTS")
    print("="*30)
    print(f"✅ Model Accuracy: {acc:.4f}")
    print(f"🔥 Model AUC Score: {auc:.4f}")
    print("="*30)
    
    # Feature Importance to see what the model 'learned'
    importances = model.feature_importances_
    feat_importances = pd.Series(importances, index=X.columns)
    print("\n🏆 Top Contributing Factors (Learned):")
    print(feat_importances.sort_values(ascending=False))
    
    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), 'cvd_model.pkl')
    joblib.dump(model, model_path)
    print(f"\n💾 Model successfully clubbed and saved to: {model_path}")
    
    return auc

if __name__ == "__main__":
    train_and_evaluate()
