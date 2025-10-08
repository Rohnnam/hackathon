import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_personality_scores(personality_answers):
    traits = {
        'Openness': [1, 2, 3, 4],  # 4 is reverse
        'Conscientiousness': [5, 6, 7, 8],  # 8 reverse
        'Extraversion': [9, 10, 11, 12],  # 12 reverse
        'Agreeableness': [13, 14, 15, 16],  # 16 reverse
        'Neuroticism': [17, 18, 19, 20]  # 20 reverse
    }
    reverse_questions = [4, 8, 12, 16, 20]
    
    scores = {}
    for trait, questions in traits.items():
        trait_scores = []
        for q in questions:
            answer = personality_answers.get(str(q), 5)
            if q in reverse_questions:
                trait_scores.append(11 - answer)
            else:
                trait_scores.append(answer)
        scores[trait] = sum(trait_scores) / len(trait_scores)
    
    return scores

def summarize_user_profile(raw_data):
    personality_scores = compute_personality_scores(raw_data.get('personality_answers', {}))
    skills = raw_data.get('skills', [])
    interests = raw_data.get('interests', [])
    open_ended = raw_data.get('open_ended', [])
    
    summary = {
        'personality': personality_scores,
        'skills': skills,
        'interests': interests,
        'open_ended_themes': ' '.join(open_ended),
        'preferences': raw_data.get('preferences', {})
    }
    return summary

def add_similarity_scores(recommendations, user_skills, job_dataset):
    if not user_skills:
        return recommendations
    
    # Simple synonym mapping for skills
    skill_synonyms = {
        'problem-solving': 'critical thinking',
        'communication': 'speaking',
        'design thinking': 'creativity'
    }
    
    # Normalize user skills with synonyms
    normalized_user_skills = []
    for skill in user_skills:
        normalized_user_skills.append(skill.lower())
        if skill.lower() in skill_synonyms:
            normalized_user_skills.append(skill_synonyms[skill.lower()])
    user_skills_text = ' '.join(normalized_user_skills)
    print(f"Normalized user skills: {normalized_user_skills}")  # Debug
    
    # Normalize job skills and create mapping of normalized career names
    job_texts = {}
    career_mapping = {}
    for job in job_dataset:
        career = job['career'].lower()
        # Remove plural suffixes for matching
        if career.endswith('es'):
            normalized_career = career[:-2]
        elif career.endswith('s'):
            normalized_career = career[:-1]
        else:
            normalized_career = career
        career_mapping[normalized_career] = job['career']
        # Normalize job skills with synonyms
        normalized_job_skills = []
        for skill in job['core_skills']:
            normalized_job_skills.append(skill.lower())
            if skill.lower() in skill_synonyms:
                normalized_job_skills.append(skill_synonyms[skill.lower()])
        job_texts[job['career']] = ' '.join(normalized_job_skills)
        print(f"Normalized skills for {job['career']}: {normalized_job_skills}")  # Debug
    
    vectorizer = TfidfVectorizer()
    all_texts = [user_skills_text] + list(job_texts.values())
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    feature_names = vectorizer.get_feature_names_out()
    print(f"TF-IDF features: {list(feature_names)}")  # Debug
    
    user_vector = tfidf_matrix[0]
    for rec in recommendations:
        career = rec['career'].lower()
        # Normalize career name for matching
        if career.endswith('es'):
            normalized_career = career[:-2]
        elif career.endswith('s'):
            normalized_career = career[:-1]
        else:
            normalized_career = career
        
        if normalized_career in career_mapping:
            original_career = career_mapping[normalized_career]
            job_vector = tfidf_matrix[list(job_texts.keys()).index(original_career) + 1]
            similarity = cosine_similarity(user_vector, job_vector)[0][0]
            # Boost score for synonym or exact matches
            job_skills = job_texts[original_career].split()
            has_match = any(skill in user_skills_text for skill in job_skills) or \
                        any(syn in job_skills for user_skill in user_skills for syn in [skill_synonyms.get(user_skill.lower(), '')])
            rec['match_score'] = round(similarity * 100 * 2.0 if has_match else similarity * 100, 2)
            print(f"Similarity score for {rec['career']}: {rec['match_score']} (Match: {has_match})")  # Debug
        else:
            rec['match_score'] = 0
            print(f"Warning: Career '{rec['career']}' not found in job_dataset.json")  # Debug
    
    recommendations.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    return recommendations