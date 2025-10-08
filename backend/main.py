import sys
import os
import json
import requests
import re
from flask import Flask, request, jsonify
from prompts import career_prompt
from utils import summarize_user_profile, add_similarity_scores

# Set CWD to the directory of this file (backend/)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Current working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Load job dataset once
try:
    with open('job_dataset.json', 'r') as f:
        job_dataset = json.load(f)
    if not job_dataset:
        raise ValueError("job_dataset.json is empty")
except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
    print(f"Error loading job_dataset.json: {str(e)}")
    exit(1)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Step 2-3: Compute scores and summarize
        user_profile = summarize_user_profile(data)
        
        # Step 4: Job data already loaded
        
        # Step 5: Build prompt
        prompt = career_prompt.format(
            user_profile=json.dumps(user_profile, indent=2),
            job_data=json.dumps(job_dataset, indent=2)
        )
        print("Formatted prompt:")  # Debug
        print(prompt)
        print("-" * 50)
        
        # Step 6: Call LLM API with retry
        try:
            headers = {
                "Authorization": "Bearer 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",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            for attempt in range(3):
                try:
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=10)
                    res.raise_for_status()
                    response_text = res.json()["choices"][0]["message"]["content"]
                    print("Raw LLM response:")  # Debug
                    print(response_text)
                    print("-" * 50)
                    break
                except requests.RequestException as e:
                    print(f"API error on attempt {attempt + 1}: {str(e)}")
                    if attempt == 2:
                        raise
            # Clean response
            cleaned_text = re.sub(r'^```json\n|```$', '', response_text, flags=re.MULTILINE).strip()
            cleaned_text = re.sub(r'^\s*[\w\s:]*\n', '', cleaned_text, flags=re.MULTILINE)
            print("Cleaned LLM response:")  # Debug
            print(cleaned_text)
            print("-" * 50)
            
        except requests.RequestException as e:
            print(f"Final API error after retries: {str(e)}")
            # Define fallback response
            fallback_response = {
                "recommendations": [
                    {
                        "career": "AI Product Managers",
                        "fit_reason": "Fallback: High openness and problem-solving skills align with AI-driven roles.",
                        "ai_impact": "AI automates data tasks, but human vision is key.",
                        "learning_path": "Learn product management, AI ethics, data literacy, leadership skills"
                    },
                    {
                        "career": "UX Designers",
                        "fit_reason": "Fallback: Creativity and empathy suit user-centric design.",
                        "ai_impact": "AI enhances prototyping, but human empathy drives design.",
                        "learning_path": "Study UX design, prototyping tools, user research, AI-UX integration"
                    },
                    {
                        "career": "Data Ethicist",
                        "fit_reason": "Fallback: High agreeableness fits roles ensuring ethical AI use.",
                        "ai_impact": "AI requires ethical oversight, but human judgment is key.",
                        "learning_path": "Study ethics, data governance, AI principles, communication skills"
                    }
                ]
            }
            response_text = json.dumps(fallback_response)
            cleaned_text = response_text
            print(f"Using fallback response: {cleaned_text}")
        
        # Step 7: Parse response
        try:
            llm_output = json.loads(cleaned_text)
            recommendations = llm_output.get("recommendations", [])
            print("Parsed JSON:")  # Debug
            print(json.dumps(llm_output, indent=2))
            if not recommendations:
                raise ValueError("No recommendations in LLM output")
            # Ensure exactly 3 recommendations
            if len(recommendations) != 3:
                print(f"Warning: Expected 3 recommendations, got {len(recommendations)}")  # Debug
                # Pad with fallback if fewer than 3
                fallback_careers = [
                    {
                        "career": "AI Product Managers",
                        "fit_reason": "Fallback: High openness and problem-solving skills align with AI-driven roles.",
                        "ai_impact": "AI automates data tasks, but human vision is key.",
                        "learning_path": "Learn product management, AI ethics, data literacy, leadership skills"
                    },
                    {
                        "career": "UX Designers",
                        "fit_reason": "Fallback: Creativity and empathy suit user-centric design.",
                        "ai_impact": "AI enhances prototyping, but human empathy drives design.",
                        "learning_path": "Study UX design, prototyping tools, user research, AI-UX integration"
                    },
                    {
                        "career": "Data Ethicist",
                        "fit_reason": "Fallback: High agreeableness fits roles ensuring ethical AI use.",
                        "ai_impact": "AI requires ethical oversight, but human judgment is key.",
                        "learning_path": "Study ethics, data governance, AI principles, communication skills"
                    }
                ]
                existing_careers = {rec.get("career", "") for rec in recommendations}
                for fallback in fallback_careers:
                    if len(recommendations) >= 3:
                        break
                    if fallback["career"] not in existing_careers:
                        recommendations.append(fallback)
                        existing_careers.add(fallback["career"])
            # Validate recommendation fields
            for rec in recommendations:
                required_fields = ["career", "fit_reason", "ai_impact", "learning_path"]
                for field in required_fields:
                    if field not in rec or not rec[field]:
                        print(f"Warning: Missing or empty field '{field}' in recommendation: {rec}")  # Debug
                        rec[field] = f"Fallback: Missing {field}"
                if isinstance(rec.get("learning_path"), list):
                    rec["learning_path"] = ", ".join(rec["learning_path"])
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {str(e)}")
            json_match = re.search(r'\{.*?\}', cleaned_text, re.DOTALL)
            if json_match:
                try:
                    llm_output = json.loads(json_match.group(0))
                    recommendations = llm_output.get("recommendations", [])
                    print("Regex-extracted JSON:")  # Debug
                    print(json.dumps(llm_output, indent=2))
                    for rec in recommendations:
                        required_fields = ["career", "fit_reason", "ai_impact", "learning_path"]
                        for field in required_fields:
                            if field not in rec or not rec[field]:
                                print(f"Warning: Missing or empty field '{field}' in recommendation: {rec}")  # Debug
                                rec[field] = f"Fallback: Missing {field}"
                        if isinstance(rec.get("learning_path"), list):
                            rec["learning_path"] = ", ".join(rec["learning_path"])
                    if len(recommendations) != 3:
                        print(f"Warning: Expected 3 recommendations, got {len(recommendations)}")  # Debug
                        existing_careers = {rec.get("career", "") for rec in recommendations}
                        for fallback in [
                            {
                                "career": "AI Product Managers",
                                "fit_reason": "Fallback: Error parsing LLM response",
                                "ai_impact": "AI automates data tasks, but human vision is key.",
                                "learning_path": "Learn product management, AI ethics, data literacy, leadership skills"
                            },
                            {
                                "career": "UX Designers",
                                "fit_reason": "Fallback: Error parsing LLM response",
                                "ai_impact": "AI enhances prototyping, but human empathy drives design.",
                                "learning_path": "Study UX design, prototyping tools, user research, AI-UX integration"
                            },
                            {
                                "career": "Data Ethicist",
                                "fit_reason": "Fallback: Error parsing LLM response",
                                "ai_impact": "AI requires ethical oversight, but human judgment is key.",
                                "learning_path": "Study ethics, data governance, AI principles, communication skills"
                            }
                        ]:
                            if len(recommendations) >= 3:
                                break
                            if fallback["career"] not in existing_careers:
                                recommendations.append(fallback)
                                existing_careers.add(fallback["career"])
                except json.JSONDecodeError as e2:
                    print(f"Regex JSON parse failed: {str(e2)}")
                    recommendations = [
                        {
                            "career": "AI Product Managers",
                            "fit_reason": "Fallback: Error parsing LLM response",
                            "ai_impact": "AI automates data tasks, but human vision is key.",
                            "learning_path": "Learn product management, AI ethics, data literacy, leadership skills"
                        },
                        {
                            "career": "UX Designers",
                            "fit_reason": "Fallback: Error parsing LLM response",
                            "ai_impact": "AI enhances prototyping, but human empathy drives design.",
                            "learning_path": "Study UX design, prototyping tools, user research, AI-UX integration"
                        },
                        {
                            "career": "Data Ethicist",
                            "fit_reason": "Fallback: Error parsing LLM response",
                            "ai_impact": "AI requires ethical oversight, but human judgment is key.",
                            "learning_path": "Study ethics, data governance, AI principles, communication skills"
                        }
                    ]
            else:
                recommendations = [
                    {
                        "career": "AI Product Managers",
                        "fit_reason": "Fallback: No JSON found in response",
                        "ai_impact": "AI automates data tasks, but human vision is key.",
                        "learning_path": "Learn product management, AI ethics, data literacy, leadership skills"
                    },
                    {
                        "career": "UX Designers",
                        "fit_reason": "Fallback: No JSON found in response",
                        "ai_impact": "AI enhances prototyping, but human empathy drives design.",
                        "learning_path": "Study UX design, prototyping tools, user research, AI-UX integration"
                    },
                    {
                        "career": "Data Ethicist",
                        "fit_reason": "Fallback: No JSON found in response",
                        "ai_impact": "AI requires ethical oversight, but human judgment is key.",
                        "learning_path": "Study ethics, data governance, AI principles, communication skills"
                    }
                ]
            print(f"Using fallback recommendations: {json.dumps(recommendations, indent=2)}")
        
        # Step 8: Add similarity scores and re-rank
        user_skills = user_profile.get('skills', [])
        print(f"User skills: {user_skills}")  # Debug
        print(f"Recommended careers: {[rec['career'] for rec in recommendations]}")  # Debug
        recommendations = add_similarity_scores(recommendations, user_skills, job_dataset)
        print(f"Recommendations with similarity scores: {json.dumps(recommendations, indent=2)}")  # Debug
        
        # Step 9: Send back
        return jsonify({
            "recommendations": recommendations,
            "personality_summary": user_profile['personality']
        })
    
    except Exception as e:
        print(f"Internal error: {str(e)}")
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(port=8000, debug=True)