import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
import joblib
import os
import itertools

def generate_extraordinary_data(n=100000):
    """
    Generates 100,000 synthetic CVD cases with 'weird and extraordinary' variations.
    Uses combinations of risk factors.
    Includes:
    - Pediatric hypertension/tachycardia (age < 15)
    - Geriatric outliers (age > 90)
    - Women specific cases
    - Athlete anomalies (low HR with sudden BP spikes)
    - Silent symptoms (high risk vitals with no pain)
    - BMI/Vitals mismatch (Low BMI with high BP)
    """
    print(f"Generating {n} cases...")
    np.random.seed(42)
    
    # Generate base populations
    ages = np.random.randint(5, 100, size=n)
    sexes = np.random.choice([0, 1], size=n) # 0: Female, 1: Male
    bmis = np.random.uniform(15, 45, size=n)
    hrs = np.random.randint(40, 160, size=n)
    sbps = np.random.randint(80, 200, size=n)
    dbps = np.random.randint(50, 120, size=n)
    chest_pains = np.random.choice([0, 1], p=[0.7, 0.3], size=n)
    sob = np.random.choice([0, 1], p=[0.8, 0.2], size=n)
    
    df = pd.DataFrame({
        'age': ages,
        'sex': sexes,
        'bmi': bmis,
        'hr': hrs,
        'sbp': sbps,
        'dbp': dbps,
        'chest_pain': chest_pains,
        'shortness_of_breath': sob
    })
    
    risk_scores = np.zeros(n)
    
    # 1. Pediatric Risk
    mask_pediatric = df['age'] < 18
    risk_scores[mask_pediatric & (df['hr'] > 115)] += 1.5
    risk_scores[mask_pediatric & (df['sbp'] > 140)] += 1.5
    
    # 2. Geriatric Risk
    mask_geriatric = df['age'] > 80
    risk_scores[mask_geriatric & (df['hr'] < 55)] += 1.0
    risk_scores[mask_geriatric] += 0.5
    
    # 3. Women specific (e.g. higher risk for post-menopausal with hypertension)
    mask_women = df['sex'] == 0
    risk_scores[mask_women & (df['age'] > 55) & (df['sbp'] > 130)] += 1.2
    # Women with silent symptoms
    risk_scores[mask_women & (df['chest_pain'] == 0) & (df['shortness_of_breath'] == 1) & (df['age'] > 45)] += 1.5
    
    # 4. Vitals Thresholds
    risk_scores[df['hr'] > 140] += 2.0
    risk_scores[df['hr'] < 40] += 1.5
    risk_scores[df['sbp'] > 175] += 1.8
    risk_scores[df['dbp'] > 110] += 1.2
    
    # 5. Silent Killers: No pain but high BP and age
    risk_scores[(df['chest_pain'] == 0) & (df['sbp'] > 165) & (df['age'] > 65)] += 1.5
    
    # 6. The "Athlete" Extraordinary Case
    risk_scores[(df['hr'] < 45) & ((df['bmi'] > 28) | (df['sbp'] > 150))] += 2.2
    
    # 7. BMI/Vitals Paradox
    risk_scores[(df['bmi'] < 19) & (df['sbp'] > 155)] += 1.7
    
    # Cumulative symptoms
    risk_scores[(df['chest_pain'] == 1) & (df['shortness_of_breath'] == 1)] += 1.2
    mask_either = (df['chest_pain'] == 1) ^ (df['shortness_of_breath'] == 1)
    risk_scores[mask_either] += 0.6
    
    # Male nuances
    risk_scores[(df['sex'] == 1) & (df['age'] > 50) & (df['sbp'] > 140)] += 0.5
    
    probs = 1 / (1 + np.exp(- (risk_scores - 2.5))) 
    df['target'] = (probs > 0.5).astype(int)
    
    return df

def train_and_evaluate():
    print("🚀 Initializing CardioGuard AI Model Training Pipeline...")
    print("📊 Generating 100,000 complex CVD cases...")
    df = generate_extraordinary_data(100000)
    
    # Save dataset for reference
    data_path = os.path.join(os.path.dirname(__file__), 'extraordinary_cvd_data.csv')
    df.to_csv(data_path, index=False)
    print(f"✅ Data saved to {data_path}")
    
    # Split Data
    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model Training
    print("🧠 Training Random Forest Classifier on comprehensive dataset...")
    # Adjusting n_estimators slightly down to keep training time reasonable for 100k, but still highly accurate
    model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=15, 
        min_samples_split=5,
        n_jobs=-1, # use all cores
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
    print(f"\n💾 Model successfully built and saved to: {model_path}")
    
    return auc

if __name__ == "__main__":
    train_and_evaluate()
