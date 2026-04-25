from core.llm_engine import ask_llm_json

def generate_training_plan(unmatched_skills):
    """Generates Report C: The Training Plan for missing skills."""
    skills_list = [s["name"] for s in unmatched_skills]
    if not skills_list:
        return {"plan":[]}

    prompt = f"""
    Create a practical training plan for these missing skills: {skills_list}
    Return exactly this JSON format:
    {{
        "plan":[
            {{"skill": "Skill Name", "content": "Course or tutorial name", "duration": "X weeks"}}
        ]
    }}
    """
    return ask_llm_json(prompt)

def evaluate_interview_answers(transcript_dict):
    """Sends the voice transcript to the LLM to grade the candidate's actual knowledge."""
    prompt = f"""
    You are a strict technical hiring manager. Evaluate the candidate's answers from their voice interview.
    If the answer contains "No response", "Timeout", is empty, or shows poor knowledge, you MUST grade it as "Fail".

    Transcript:
    {transcript_dict}

    Return EXACTLY this JSON structure:
    {{
        "grades":[
            {{"skill": "Skill Name", "grade": "Pass or Fail", "feedback": "One short sentence explaining why"}}
        ]
    }}
    """
    return ask_llm_json(prompt)

def compile_all_reports(analysis_results, training_plan, interview_transcript, interview_grades):
    """Assembles all reports into a final dictionary."""
    return {
        "Report_A_Skill_Match": analysis_results["matched"] + analysis_results["unmatched"],
        "Report_B_Summary": {
            "Total_Matched": len(analysis_results["matched"]),
            "Total_Unmatched": len(analysis_results["unmatched"]),
            "Resume_Fit_Score": analysis_results["score_percentage"],
            "Interview_Transcript": interview_transcript,
            "Interview_Grades": interview_grades.get("grades",[])
        },
        "Report_C_Training_Plan": training_plan.get("plan",[])
    }
