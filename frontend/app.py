import streamlit as st
import requests
import json
from questions import personality_questions, structured_questions, open_questions

# Backend URL (update with your hosted backend URL, e.g., from Render or Replit)
BACKEND_URL = "http://localhost:8000/predict"  # Replace with https://your-backend.render.com/predict after hosting

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"  # Start on home page
if "answers_personality" not in st.session_state:
    st.session_state.answers_personality = {}
if "answers_structured" not in st.session_state:
    st.session_state.answers_structured = {}
if "answers_open" not in st.session_state:
    st.session_state.answers_open = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

# Helper function to convert personality answers to numeric scores
def convert_to_numeric(answer, is_reverse=False):
    """Convert personality answer to numeric score (1-10 scale)"""
    score_map = {
        "Strongly Agree": 9,
        "Agree": 7,
        "Neutral": 5,
        "Disagree": 3,
        "Strongly Disagree": 1  # Fixed typo: "Strongly Dissagree" to "Strongly Disagree"
    }
    score = score_map.get(answer, 5)
    if is_reverse:
        score = 10 - score
    return score

# Home / Start Page
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;color:#4B8BBE;'>SkillSync</h1>", unsafe_allow_html=True)
    st.write("Find careers that AI will empower HUMANS, not replace.")
    st.write("\n")
    
    if st.button("Start Test"):
        st.session_state.page = "questions"
        st.rerun()

# Questions Page
if st.session_state.page == "questions":
    st.markdown("## Personality Questions")
    st.write("Answer on a scale: Strongly Agree → Strongly Disagree")

    # Personality questions
    for idx, q in enumerate(personality_questions):
        question_num = idx + 1
        ans = st.radio(
            q["question"],
            ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"],
            key=f"p_{idx}",
            horizontal=True
        )
        st.session_state.answers_personality[str(question_num)] = ans

    st.markdown("---")

    # Structured questions
    st.markdown("## Structured Questions")
    for idx, q in enumerate(structured_questions):
        key = f"s_{idx}"
        if q["type"] == "single":
            ans = st.selectbox(q["question"], q["options"], key=key)
        elif q["type"] == "multi":
            ans = st.multiselect(q["question"], q["options"], key=key)
        elif q["type"] == "text":
            ans = st.text_area(q["question"], key=key)
        st.session_state.answers_structured[q["question"]] = ans

    st.markdown("---")

    # Open-ended questions
    st.markdown("## Open-Ended Questions")
    for idx, q in enumerate(open_questions):
        ans = st.text_area(q, key=f"o_{idx}")
        if ans:
            if len(st.session_state.answers_open) <= idx:
                st.session_state.answers_open.append(ans)
            else:
                st.session_state.answers_open[idx] = ans

    st.markdown("---")

    # Submit button
    if st.button("Submit"):
        # Convert personality answers to numeric scores
        personality_numeric = {}
        for idx, q in enumerate(personality_questions):
            question_num = str(idx + 1)
            answer = st.session_state.answers_personality.get(question_num, "Neutral")
            is_reverse = "(reverse)" in q["question"]
            personality_numeric[question_num] = convert_to_numeric(answer, is_reverse)
        
        # Extract skills
        skills_raw = st.session_state.answers_structured.get(
            "What skills do you believe you are strongest at?", []
        )
        skills = [skill.lower().replace(" / ", "_").replace(" ", "_") for skill in skills_raw]
        
        # Extract interests
        interests_raw = st.session_state.answers_structured.get(
            "What domains / fields interest you most?", []
        )
        interests = [interest.lower().replace(" / ", "_").replace(" ", "_") for interest in interests_raw]
        
        # Extract preferences
        work_env = st.session_state.answers_structured.get(
            "Which setting would you prefer to work in?", ""
        )
        dream_jobs = st.session_state.answers_structured.get(
            '(Optional) What are your top 2 "dream" job ideas or roles you admire?', ""
        )
        
        preferences = {
            "work_environment": work_env.lower().replace(" / ", "_").replace(" ", "_") if work_env else "",
            "dream_roles": dream_jobs
        }
        
        # Compile open-ended responses
        open_ended_responses = [ans for ans in st.session_state.answers_open if ans.strip()]
        
        # Final formatted data
        user_data = {
            "name": "User Submission",
            "data": {
                "personality_answers": personality_numeric,
                "skills": skills,
                "interests": interests,
                "open_ended": open_ended_responses,
                "preferences": preferences
            }
        }
        
        # Send to backend
        try:
            response = requests.post(BACKEND_URL, json=user_data, timeout=10)
            if response.status_code == 200:
                st.session_state.recommendations = response.json()
                st.session_state.page = "results"
                st.rerun()
            else:
                st.error(f"Backend error: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            st.error(f"Failed to connect to backend: {str(e)}")
        
        st.success("✓ Your answers have been collected!")
        st.json(user_data)

# Results Page
if st.session_state.page == "results" and st.session_state.recommendations:
    st.markdown("<h1 style='text-align:center;color:#4B8BBE;'>Your Career Recommendations</h1>", unsafe_allow_html=True)
    st.write("Based on your personality, skills, and interests, here are your top career matches:")
    
    recommendations = st.session_state.recommendations.get("recommendations", [])
    personality_summary = st.session_state.recommendations.get("personality_summary", {})
    
    # Display personality summary
    st.markdown("### Your Personality Summary")
    for trait, score in personality_summary.items():
        st.write(f"**{trait}**: {score}")
    
    # Display recommendations as cards
    st.markdown("### Your Career Matches")
    for rec in recommendations:
        with st.container():
            st.markdown(f"""
                <div style='border:1px solid #ccc;padding:15px;border-radius:10px;margin:10px 0;'>
                    <h3>{rec['career']}</h3>
                    <p><strong>Match Score:</strong> {rec['match_score']:.2f}%</p>
                    <p><strong>Why It Fits:</strong> {rec['fit_reason']}</p>
                    <p><strong>AI Impact:</strong> {rec['ai_impact']}</p>
                    <p><strong>Learning Path:</strong> {rec['learning_path']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.session_state.recommendations = None
        st.rerun()