import requests
import json

# API endpoint
url = "http://127.0.0.1:8000/analyze"

# Input data
data = {
    "age": 45,
    "gender": "Male",
    "height": 175,
    "weight": 85,
    "bmi": 27.8,
    "smoking_level": "regular",
    "alcohol_level": "moderate",
    "diet_type": "balanced",
    "physical_activity": 3,
    "sleep_hours": 6,
    "stress_level": 7,
    "medical_history": "heart disease"
}

print("\n" + "="*60)
print("🧠 Life Risk Analyzer - API Test")
print("="*60)
print(f"\n📡 Sending request to: {url}")
print(f"📋 Input data: {json.dumps(data, indent=2)}")

try:
    # Send POST request
    response = requests.post(url, json=data, timeout=10)
    
    print(f"\n✓ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        predictions = result.get("predictions", {})
        recommendations = result.get("recommendations", [])
        
        print("\n" + "="*60)
        print("📊 DISEASE RISK PREDICTIONS")
        print("="*60)
        
        for disease, models in predictions.items():
            print(f"\n🏥 {disease.upper()}:")
            
            rf_data = models.get("rf", {})
            lr_data = models.get("lr", {})
            
            # Random Forest
            rf_pred = "High Risk" if rf_data.get("prediction") == 1 else "Low Risk"
            rf_prob = rf_data.get("probability")
            if rf_prob is not None:
                print(f"   Random Forest:      {rf_pred} ({rf_prob*100:.2f}%)")
            else:
                print(f"   Random Forest:      {rf_pred}")
            
            # Logistic Regression
            lr_pred = "High Risk" if lr_data.get("prediction") == 1 else "Low Risk"
            lr_prob = lr_data.get("probability")
            if lr_prob is not None:
                print(f"   Logistic Regression: {lr_pred} ({lr_prob*100:.2f}%)")
            else:
                print(f"   Logistic Regression: {lr_pred}")
        
        print("\n" + "="*60)
        print("💡 LIFESTYLE RECOMMENDATIONS")
        print("="*60)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*60)
        print("✓ Test completed successfully!")
        print("="*60 + "\n")
    
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR!")
    print("The API server is not running.")
    print("\nTo start the API, run in a separate terminal:")
    print("   python -m uvicorn src.api:app --reload")
    print("="*60 + "\n")

except requests.exceptions.Timeout:
    print("\n❌ REQUEST TIMEOUT!")
    print("The API took too long to respond.")
    print("="*60 + "\n")

except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("="*60 + "\n")