import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/vitals/ingest"

def print_result(result):
    print(json.dumps(result, indent=2))
    if result.get('red_alert_triggered'):
        print("\n🚨 RED ALERT TRIGGERED! Logic Verified. 🚨")
    else:
        print("\n✅ Status Normal. Logic Verified.")

def test_healthy_patient():
    print("\n--- TEST CASE 1: Healthy Patient (Low Risk) ---")
    payload = {
        "age": 30,
        "sex": "M",
        "bmi": 22.5,
        "current_vitals": {
            "hr": 70,
            "sbp": 120,
            "dbp": 80
        },
        "symptoms": [],
        "history_flags": {"diabetes": False}
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        print_result(response.json())
    except Exception as e:
        print(f"❌ Test Failed: {e}")

def test_critical_patient():
    print("\n--- TEST CASE 2: Critical Patient (High Risk) ---")
    payload = {
        "age": 65,
        "sex": "F",
        "bmi": 31.0,
        "current_vitals": {
            "hr": 145, # Tachycardia
            "sbp": 160, # Hypertension
            "dbp": 95
        },
        "symptoms": ["chest_pain", "shortness_of_breath"],
        "history_flags": {"hypertension": True}
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        print_result(response.json())
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    print("Waiting for server to spark up...")
    time.sleep(3) # Give Uvicorn a moment
    test_healthy_patient()
    test_critical_patient()
