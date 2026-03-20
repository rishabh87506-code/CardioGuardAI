import requests
import json
import time

PROXY_URL = "http://localhost:5006/api/predict"

SCENARIOS = [
    {
        "name": "Low Risk (Young/Healthy)",
        "payload": {
            "age": 25, "sex": 1, "cholesterol": 170, "blood_pressure": 115, "heart_rate": 65,
            "diabetes": 0, "family_history": 0, "smoking": 0, "obesity": 0, "alcohol_consumption": 0,
            "exercise_hours_per_week": 6, "diet": 2, "previous_heart_problems": 0, "medication_use": 0,
            "stress_level": 2, "sedentary_hours_per_day": 4, "bmi": 21, "triglycerides": 120,
            "physical_activity_days_per_week": 5, "sleep_hours_per_day": 8, "chest_pain": 0, "blood_sugar": 85
        }
    },
    {
        "name": "Moderate Risk (Middle-Age/Warning)",
        "payload": {
            "age": 48, "sex": 0, "cholesterol": 210, "blood_pressure": 138, "heart_rate": 78,
            "diabetes": 0, "family_history": 1, "smoking": 0, "obesity": 0, "alcohol_consumption": 1,
            "exercise_hours_per_week": 2, "diet": 1, "previous_heart_problems": 0, "medication_use": 1,
            "stress_level": 6, "sedentary_hours_per_day": 8, "bmi": 26, "triglycerides": 160,
            "physical_activity_days_per_week": 2, "sleep_hours_per_day": 6, "chest_pain": 0, "blood_sugar": 105
        }
    },
    {
        "name": "High Risk (Senior/Critical)",
        "payload": {
            "age": 68, "sex": 1, "cholesterol": 280, "blood_pressure": 175, "heart_rate": 92,
            "diabetes": 1, "family_history": 1, "smoking": 1, "obesity": 1, "alcohol_consumption": 1,
            "exercise_hours_per_week": 0, "diet": 0, "previous_heart_problems": 1, "medication_use": 1,
            "stress_level": 9, "sedentary_hours_per_day": 12, "bmi": 34, "triglycerides": 240,
            "physical_activity_days_per_week": 0, "sleep_hours_per_day": 5, "chest_pain": 1, "blood_sugar": 160
        }
    }
]

def run_tests():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     CardioGuard AI — Clinical Scenario Test Suite        ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    for s in SCENARIOS:
        print(f"Testing Scenario: {s['name']}")
        try:
            start_time = time.time()
            response = requests.post(PROXY_URL, json=s['payload'], timeout=10)
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Status: SUCCESS ({elapsed:.0f}ms)")
                print(f"  🧠 Risk Score: {data.get('risk_score', 'N/A')}")
                print(f"  📋 Risk Level: {data.get('risk_level', 'N/A')}")
                
                # Check SHAP factors to ensure interpretability is working
                shap = data.get('shap_values', {})
                if shap:
                    top_factor = max(shap, key=lambda k: shap[k]['impact'])
                    print(f"  ⚖️  Top Feature Impact: {top_factor} ({shap[top_factor]['impact']:.2f}%)")
                
                print(f"  🌐 Proxy Routing: {data.get('proxy_mode', 'True')}")
            else:
                print(f"  ✗ Status: FAILED ({response.status_code})")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"  ✗ Status: ERROR")
            print(f"  Exception: {str(e)}")
        print("─" * 60)

if __name__ == "__main__":
    run_tests()
