# Personality Questions (OCEAN)
personality_questions = [
    {"question": "I have a vivid imagination.", "trait": "Openness"},
    {"question": "I often try new and foreign things (ideas, foods, places).", "trait": "Openness"},
    {"question": "I enjoy reflecting on things and self-analysis.", "trait": "Openness"},
    {"question": "I prefer routine over new experiences. (reverse)", "trait": "Openness"},
    {"question": "I am always prepared / plan ahead.", "trait": "Conscientiousness"},
    {"question": "I pay attention to details.", "trait": "Conscientiousness"},
    {"question": "I follow a schedule.", "trait": "Conscientiousness"},
    {"question": "I often procrastinate or leave things to last minute. (reverse)", "trait": "Conscientiousness"},
    {"question": "I feel comfortable around people / enjoy social situations.", "trait": "Extraversion"},
    {"question": "I talk to a lot of different people at parties / gatherings.", "trait": "Extraversion"},
    {"question": "I prefer being the center of attention.", "trait": "Extraversion"},
    {"question": "I keep in the background in social gatherings. (reverse)", "trait": "Extraversion"},
    {"question": "I sympathize with others’ feelings.", "trait": "Agreeableness"},
    {"question": "I take time out for others.", "trait": "Agreeableness"},
    {"question": "I tend to treat others well / with kindness.", "trait": "Agreeableness"},
    {"question": "I often criticize or judge others harshly. (reverse)", "trait": "Agreeableness"},
    {"question": "I get stressed out easily.", "trait": "Neuroticism"},
    {"question": "I often feel anxious or worry about things.", "trait": "Neuroticism"},
    {"question": "I moodily go from high to low.", "trait": "Neuroticism"},
    {"question": "I remain calm under pressure. (reverse)", "trait": "Neuroticism"},
]

# Structured / choice questions
structured_questions = [
    {
        "question": "What domains / fields interest you most?",
        "type": "multi",
        "options": ["Technology / AI / Software", "Design / Creative arts", "Business / Management", 
                    "Education / Research", "Healthcare / Biology", "Writing / Communication",
                    "Social services / Psychology", "Engineering / Mechanics", "Others: ___"]
    },
    {
        "question": "What skills do you believe you are strongest at?",
        "type": "multi",
        "options": ["Programming / coding", "Data analysis / statistics", "Creative thinking / ideation",
                    "Communication / writing", "Team leadership", "Design / user experience",
                    "Emotional intelligence / empathy", "Project management",
                    "Domain knowledge (science, finance, etc.)", "Others: ___"]
    },
    {
        "question": "Which setting would you prefer to work in?",
        "type": "single",
        "options": ["Remote / distributed", "Office / co-located team", "Fieldwork / lab / on-site",
                    "Academia / research environment", "Startups / fast-paced", "Large organization / stable"]
    },
    {
        "question": "(Optional) What are your top 2 “dream” job ideas or roles you admire?",
        "type": "text"
    }
]

# Open-ended questions
open_questions = [
    "What work / activity has given you the greatest joy or satisfaction?",
    "Describe a project or task you did where you were deeply focused and lost track of time.",
    "What frustrates you most when working (in jobs or school)?",
    "What are your greatest strengths (in your own words)?",
    "What weaknesses do you feel you need to improve?",
    "If you could pick any skill to master in your lifetime, what would it be and why?",
    "What problem in the world do you want to help solve (if any)?",
    "Describe your ideal work environment / day.",
    "What fears or limiting beliefs hold you back?",
    "What would make a job feel meaningful to you?"
]
