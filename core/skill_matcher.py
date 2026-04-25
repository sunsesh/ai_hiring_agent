from core.llm_engine import ask_llm_json

def extract_jd_skills(jd_text):
    """Extracts skills and assigns a weight (1-5) based on importance."""
    prompt = f"""
    Analyze this Job Description. Extract technical and soft skills.
    Assign a weight from 1 to 5 for each skill based on how important it is (5 = Crucial, 1 = Low).

    Return EXACTLY this JSON structure:
    {{
        "technical_skills":[ {{"name": "Skill", "weight": 5}} ],
        "soft_skills":[ {{"name": "Skill", "weight": 4}} ]
    }}

    JD Text:
    {jd_text}
    """
    return ask_llm_json(prompt)

def extract_resume_skills(resume_text):
    """Extracts skills from the resume."""
    prompt = f"""
    Extract all technical and soft skills from this resume.
    Return EXACTLY this JSON structure:
    {{ "skills":["Skill 1", "Skill 2"] }}

    Resume Text:
    {resume_text}
    """
    return ask_llm_json(prompt)

def analyze_and_score(jd_skills, resume_skills_dict):
    """Scoring Algorithm: Calculates weighted fit score."""
    candidate_skills =[s.lower() for s in resume_skills_dict.get("skills", [])]

    matched_skills =[]
    unmatched_skills =[]

    total_possible_score = 0
    candidate_score = 0

    all_jd_skills = jd_skills.get("technical_skills",[]) + jd_skills.get("soft_skills",[])

    for skill_obj in all_jd_skills:
        skill_name = skill_obj["name"]
        weight = skill_obj["weight"]
        total_possible_score += weight

        # Check if JD skill exists in Candidate's skills
        is_match = any(skill_name.lower() in cs or cs in skill_name.lower() for cs in candidate_skills)

        if is_match:
            candidate_score += weight
            matched_skills.append({"name": skill_name, "weight": weight, "match": True})
        else:
            unmatched_skills.append({"name": skill_name, "weight": weight, "match": False})

    fit_score_percentage = (candidate_score / total_possible_score * 100) if total_possible_score > 0 else 0

    return {
        "matched": matched_skills,
        "unmatched": unmatched_skills,
        "score_percentage": round(fit_score_percentage, 2)
    }

def get_top_5_interview_skills(jd_skills):
    """Selects min(2 soft skills), rest technical, to equal 5 skills max."""
    soft = [s["name"] for s in sorted(jd_skills.get("soft_skills", []), key=lambda x: x["weight"], reverse=True)]
    tech =[s["name"] for s in sorted(jd_skills.get("technical_skills",[]), key=lambda x: x["weight"], reverse=True)]

    selected_soft = soft[:2] if len(soft) >= 2 else soft
    remaining_slots = 5 - len(selected_soft)
    selected_tech = tech[:remaining_slots]

    return selected_soft + selected_tech
