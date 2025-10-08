import requests
import json

# Quick test to verify the placeholder key doesn't crash
url = "http://127.0.0.1:8000/predict"

test_data = {
    "skills": ["python", "creativity"],
    "interests": ["technology"],
    "open_ended": ["I like tech"],
    "preferences": {"work_environment": "remote"}
}

print("Testing with placeholder API key...")
print("=" * 60)

try:
    response = requests.post(url, json=test_data, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ SUCCESS! Server didn't crash")
        print(f"✓ Got {len(result['recommendations'])} recommendations")
        
        # Check for fallback
        if any('Fallback' in rec.get('fit_reason', '') for rec in result['recommendations']):
            print("✓ Using fallback responses (expected with placeholder key)")
        
        # Check for empty objects
        empty_count = sum(1 for rec in result['recommendations'] if not rec or rec == {})
        if empty_count > 0:
            print(f"✗ ERROR: Found {empty_count} empty objects!")
        else:
            print("✓ No empty objects")
        
        print("\nRecommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"{i}. {rec.get('career', 'MISSING')}: {rec.get('match_score', 0)}")
    else:
        print(f"\n✗ ERROR: Got status {response.status_code}")
        print(response.json())

except requests.exceptions.RequestException as e:
    print(f"✗ Request failed: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

print("=" * 60)