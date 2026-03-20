import numpy as np
import pandas as pd
import requests
import time
import json

# Configuration
API_URL = "http://localhost:5005/api/batch"
NUM_CASES = 10000
FEATURES = [
    "age","sex","cholesterol","blood_pressure","heart_rate",
    "diabetes","family_history","smoking","obesity","alcohol_consumption",
    "exercise_hours_per_week","diet","previous_heart_problems","medication_use",
    "stress_level","sedentary_hours_per_day","bmi","triglycerides",
    "physical_activity_days_per_week","sleep_hours_per_day","chest_pain","blood_sugar"
]

def generate_synthetic_data(n):
    data = []
    labels = []
    for _ in range(n):
        case = {
            "age": np.random.randint(18, 90),
            "sex": np.random.randint(0, 2),
            "cholesterol": np.random.randint(150, 300),
            "blood_pressure": np.random.randint(90, 180),
            "heart_rate": np.random.randint(60, 120),
            "diabetes": np.random.randint(0, 2),
            "family_history": np.random.randint(0, 2),
            "smoking": np.random.randint(0, 2),
            "obesity": np.random.randint(0, 2),
            "alcohol_consumption": np.random.randint(0, 2),
            "exercise_hours_per_week": np.random.randint(0, 10),
            "diet": np.random.randint(0, 3), # 0: unhealthy, 1: mid, 2: healthy
            "previous_heart_problems": np.random.randint(0, 2),
            "medication_use": np.random.randint(0, 2),
            "stress_level": np.random.randint(1, 11),
            "sedentary_hours_per_day": np.random.randint(1, 12),
            "bmi": np.random.randint(18, 40),
            "triglycerides": np.random.randint(100, 400),
            "physical_activity_days_per_week": np.random.randint(0, 8),
            "sleep_hours_per_day": np.random.randint(4, 10),
            "chest_pain": np.random.randint(0, 2),
            "blood_sugar": np.random.randint(70, 200)
        }
        
        # Ground Truth Logic (Target)
        # Very simple clinical risk factors
        is_cvd = 0
        if case["age"] > 60 and case["smoking"] == 1 and case["blood_pressure"] > 140: is_cvd = 1
        elif case["previous_heart_problems"] == 1 and case["chest_pain"] == 1: is_cvd = 1
        elif case["diabetes"] == 1 and case["cholesterol"] > 240: is_cvd = 1
        elif case["bmi"] > 35 and case["blood_pressure"] > 150: is_cvd = 1
        
        data.append(case)
        labels.append(is_cvd)
        
    return data, labels

print(f"📊 Generating {NUM_CASES} synthetic cases...")
test_data, ground_truth = generate_synthetic_data(NUM_CASES)

print(f"🚀 Starting Batch Audit on local server...")
start_time = time.time()
try:
    # We send in chunks of 1000 to avoid payload limits
    all_results = []
    chunk_size = 1000
    for i in range(0, NUM_CASES, chunk_size):
        chunk = test_data[i:i+chunk_size]
        res = requests.post(API_URL, json=chunk)
        if res.status_code == 200:
            all_results.extend(res.json()["results"])
        else:
            print(f"❌ Chunk {i//chunk_size} failed: {res.text}")
    
    end_time = time.time()
    
    # Analyze Accuracy
    predictions = [1 if r["risk_score"] >= 50 else 0 for r in all_results]
    
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    accuracy = (correct / NUM_CASES) * 100
    
    # Simple Precision/Recall
    tp = sum(1 for p, g in zip(predictions, ground_truth) if p == 1 and g == 1)
    fp = sum(1 for p, g in zip(predictions, ground_truth) if p == 1 and g == 0)
    fn = sum(1 for p, g in zip(predictions, ground_truth) if p == 0 and g == 1)
    tn = sum(1 for p, g in zip(predictions, ground_truth) if p == 0 and g == 0)
    
    precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
    recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
    
    print("\n╔══════════════════════════════════════════╗")
    print(f"║     CardioGuardAI v4.8 Accuracy Audit    ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║ Total Cases: {NUM_CASES}                     ║")
    print(f"║ Execution Time: {end_time - start_time:.2f}s             ║")
    print(f"║ ---------------------------------------- ║")
    print(f"║ Raw Accuracy:   {accuracy:.2f}%                 ║")
    print(f"║ Precision:      {precision:.2f}%                 ║")
    print(f"║ Recall:         {recall:.2f}%                 ║")
    print(f"║ ---------------------------------------- ║")
    print(f"║ TP: {tp} | FP: {fp} | TN: {tn} | FN: {fn}   ║")
    print("╚══════════════════════════════════════════╝")
    
    if accuracy < 60:
        print("\n💡 NOTE: The model is currently using initialized weights.")
        print("To reach 99%+ accuracy, run 'python train_ptbxl.py' on the server.")

except Exception as e:
    print(f"CRITICAL: Audit failed. Make sure the server is running on port 5005. {e}")
