import requests
import json
import os

# Set the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Current working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Define the API endpoint
url = "http://127.0.0.1:8000/predict"

# Test cases
test_cases = [
    {
        "name": "Valid Input",
        "data": {
            "personality_answers": {
                "1": 8, "2": 7, "3": 6, "4": 3, "5": 9, "6": 8, "7": 7, "8": 4,
                "9": 6, "10": 5, "11": 4, "12": 3, "13": 8, "14": 7, "15": 6,
                "16": 2, "17": 4, "18": 3, "19": 5, "20": 7
            },
            "skills": ["python", "communication", "problem-solving"],
            "interests": ["technology", "helping people", "creative design"],
            "open_ended": ["I enjoy solving complex problems with technology."],
            "preferences": {"work_environment": "remote", "industry": "tech or healthcare"}
        },
        "expected_status": 200
    },
    {
        "name": "Missing Personality Answers",
        "data": {
            "skills": ["python", "communication", "problem-solving"],
            "interests": ["technology", "helping people"],
            "open_ended": ["I like working on tech projects."],
            "preferences": {"work_environment": "remote"}
        },
        "expected_status": 200
    },
    {
        "name": "Edge Case - Creativity and Empathy Skills",
        "data": {
            "skills": ["python", "creativity", "empathy"],
            "interests": ["technology", "helping people"],
            "open_ended": ["I like working on tech projects."],
            "preferences": {"work_environment": "remote"}
        },
        "expected_status": 200
    },
    {
        "name": "Empty Input",
        "data": {},
        "expected_status": 400
    }
]

print("Testing backend with multiple test cases...\n")
print("=" * 60)

for test in test_cases:
    print(f"\nRunning test case: {test['name']}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=test['data'], timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == test['expected_status']:
            print("✓ Test Passed! Status code matches expected.")
        else:
            print(f"✗ Test Failed! Expected status {test['expected_status']}, got {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                recommendations = result.get("recommendations", [])
                
                # Validate response structure
                print(f"\nNumber of recommendations: {len(recommendations)}")
                
                if len(recommendations) != 3:
                    print(f"✗ Expected 3 recommendations, got {len(recommendations)}")
                else:
                    print("✓ Correct number of recommendations")
                
                # Check each recommendation
                required_fields = ["career", "fit_reason", "ai_impact", "learning_path", "match_score"]
                for i, rec in enumerate(recommendations, 1):
                    print(f"\nRecommendation {i}:")
                    
                    # Check if it's an empty object
                    if not rec or rec == {}:
                        print(f"  ✗ ERROR: Empty recommendation object!")
                        continue
                    
                    print(f"  Career: {rec.get('career', 'MISSING')}")
                    print(f"  Match Score: {rec.get('match_score', 'MISSING')}")
                    
                    # Check for missing fields
                    missing_fields = [f for f in required_fields if f not in rec]
                    if missing_fields:
                        print(f"  ✗ Missing fields: {missing_fields}")
                    else:
                        print(f"  ✓ All required fields present")
                    
                    # Check if it's a fallback
                    if rec.get('fit_reason', '').startswith('Fallback'):
                        print(f"  ⚠ Using fallback response")
                
                # Print full JSON for reference
                print("\n" + "=" * 60)
                print("Full Response:")
                print(json.dumps(result, indent=2))
                print("=" * 60)
                
            except json.JSONDecodeError:
                print("✗ Response: Invalid JSON")
                print(response.text)
        elif response.status_code == 400:
            print(f"Error response: {response.json()}")
    
    except requests.exceptions.Timeout:
        print("✗ Request timed out after 60 seconds")
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {str(e)}")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
    
    print()

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)