import json
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.mock_data import AUTH, JOB_DESCRIPTION, RESUME_TEXT
from core.skill_matcher import (
    extract_jd_skills,
    extract_resume_skills,
    analyze_and_score,
    get_top_5_interview_skills,
)
from core.voice import conduct_voice_interview
from core.reporter import (
    generate_training_plan,
    evaluate_interview_answers,
    compile_all_reports,
)
from utils.hr_notifier import share_with_hr

st.set_page_config(page_title="AI Hiring Agent", layout="wide")

st.title("AI Hiring Agent - Candidate Portal")
st.caption("Disclaimer: AI tools were used to assist with code generation. The author reviewed, edited, and tested the code.")


def normalize_skill_list(skill_items):
    """
    Convert matched/unmatched skill data into a clean list of skill names.
    Handles strings as well as dictionaries.
    """
    normalized = []

    for item in skill_items:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict):
            if "skill" in item:
                normalized.append(str(item["skill"]))
            elif "name" in item:
                normalized.append(str(item["name"]))
            elif "Skill" in item:
                normalized.append(str(item["Skill"]))
            else:
                normalized.append(str(item))
        else:
            normalized.append(str(item))

    return normalized


# -------------------------
# Sidebar: Login + Position
# -------------------------
st.sidebar.header("Login")

job_options = {
    "Senior Backend Engineer": 1,
    "Director-Engineering": 2
}

selected_position = st.sidebar.selectbox(
    "Position Applied For",
    options=list(job_options.keys()),
    index=0
)

job_choice = job_options[selected_position]

email_input = st.sidebar.text_input("Email")
pass_input = st.sidebar.text_input("Password", type="password")

# -------------------------
# Authentication
# -------------------------
if email_input == AUTH["email"] and pass_input == AUTH["password"]:
    st.sidebar.success("Logged in successfully!")

    selected_job_description = JOB_DESCRIPTION[job_choice]

    if "job_choice" not in st.session_state:
        st.session_state.job_choice = job_choice

    if "job_description_text" not in st.session_state:
        st.session_state.job_description_text = selected_job_description

    if "resume_text" not in st.session_state:
        st.session_state.resume_text = RESUME_TEXT

    if "analysis" not in st.session_state:
        st.session_state.analysis = None

    if "interview_skills" not in st.session_state:
        st.session_state.interview_skills = None

    if "final_reports" not in st.session_state:
        st.session_state.final_reports = None

    if "interview_submitted" not in st.session_state:
        st.session_state.interview_submitted = False

    if "interview_transcript" not in st.session_state:
        st.session_state.interview_transcript = None

    if st.session_state.job_choice != job_choice:
        st.session_state.job_choice = job_choice
        st.session_state.job_description_text = JOB_DESCRIPTION[job_choice]
        st.session_state.analysis = None
        st.session_state.interview_skills = None
        st.session_state.final_reports = None
        st.session_state.interview_submitted = False
        st.session_state.interview_transcript = None

    st.write("### Review / Edit Input Data")
    col1, col2 = st.columns(2)

    with col1:
        job_description_text = st.text_area(
            "Job Description",
            value=st.session_state.job_description_text,
            height=180,
            key="job_description_editor"
        )
        st.session_state.job_description_text = job_description_text

    with col2:
        resume_text = st.text_area(
            "Candidate Resume",
            value=st.session_state.resume_text,
            height=180,
            key="resume_editor"
        )
        st.session_state.resume_text = resume_text

    st.divider()
    st.subheader("Step 1: Analyze Resume Against Job Description")

    if st.button("Analyze Candidate Fit"):
        current_job_description = st.session_state.job_description_text.strip()
        current_resume_text = st.session_state.resume_text.strip()

        if not current_job_description:
            st.error("Please choose a valid position or enter a job description.")
        elif not current_resume_text:
            st.error("Please paste or enter a resume before continuing.")
        else:
            with st.spinner("Analyzing job description and resume..."):
                jd_skills = extract_jd_skills(current_job_description)
                resume_skills = extract_resume_skills(current_resume_text)

                analysis = analyze_and_score(jd_skills, resume_skills)
                interview_skills = get_top_5_interview_skills(jd_skills)

                st.session_state.analysis = analysis
                st.session_state.interview_skills = interview_skills
                st.session_state.final_reports = None
                st.session_state.interview_submitted = False
                st.session_state.interview_transcript = None

            st.success(f"Analysis complete! Resume Fit Score: {analysis['score_percentage']}%")

    # -------------------------
    # Show analysis preview
    # -------------------------
    if st.session_state.analysis:
        analysis = st.session_state.analysis

        raw_matched_skills = analysis.get("matched", [])
        raw_unmatched_skills = analysis.get("unmatched", [])

        matched_skills = normalize_skill_list(raw_matched_skills)
        unmatched_skills = normalize_skill_list(raw_unmatched_skills)

        st.write("### Initial Analysis Summary")
        st.metric("Resume Fit Score", f"{analysis['score_percentage']}%")

        st.write("### Skill Match Overview")

        col_match, col_unmatch = st.columns(2)

        with col_match:
            st.write(f"#### ✅ Matched Skills ({len(matched_skills)})")
            if matched_skills:
                matched_df = pd.DataFrame({
                    "No.": range(1, len(matched_skills) + 1),
                    "Matched Skills": matched_skills
                })
                st.dataframe(matched_df, use_container_width=True, hide_index=True)
            else:
                st.info("No matched skills identified.")

        with col_unmatch:
            st.write(f"#### ⚠️ Missing Skills ({len(unmatched_skills)})")
            if unmatched_skills:
                unmatched_df = pd.DataFrame({
                    "No.": range(1, len(unmatched_skills) + 1),
                    "Missing Skills": unmatched_skills
                })
                st.dataframe(unmatched_df, use_container_width=True, hide_index=True)
            else:
                st.info("No missing skills identified.")

        if st.session_state.interview_skills:
            st.write("**Skills selected for interview evaluation:**")
            st.write(", ".join(map(str, st.session_state.interview_skills)))

        st.divider()
        st.subheader("Step 2: Complete AI Chat Interview")

        conduct_voice_interview(st.session_state.interview_skills)

        if st.session_state.interview_submitted and st.session_state.interview_transcript:
            st.divider()
            st.subheader("Step 3: Generate Final Evaluation Reports")

            st.info(
                "In a production deployment, the AI-generated evaluation would be shared with HR "
                "through internal enterprise workflows such as email, ATS integration, or secure file transfer. "
                "For hackathon/demo purposes only, the button below is exposed for visibility and testing. "
                "This button would not be shown to a candidate in a real candidate-facing application."
            )

            if st.button("Generate Final Reports"):
                with st.spinner("Evaluating interview answers and generating reports..."):
                    grades = evaluate_interview_answers(st.session_state.interview_transcript)
                    training = generate_training_plan(analysis["unmatched"])

                    st.session_state.final_reports = compile_all_reports(
                        analysis,
                        training,
                        st.session_state.interview_transcript,
                        grades
                    )

                st.success("Final reports generated successfully.")

    # -------------------------
    # Display Reports
    # -------------------------
    if st.session_state.final_reports:
        reports = st.session_state.final_reports

        st.divider()
        st.header("📊 Evaluation Reports")

        tab1, tab2, tab3 = st.tabs([
            "Report A: Skills Match",
            "Report B: Summary & Score",
            "Report C: Training Plan"
        ])

        with tab1:
            st.dataframe(pd.DataFrame(reports["Report_A_Skill_Match"]))

        with tab2:
            st.metric(
                "Initial Resume Fit Score",
                f"{reports['Report_B_Summary']['Resume_Fit_Score']}%"
            )
            st.write(f"**Resume Matched Skills:** {reports['Report_B_Summary']['Total_Matched']}")
            st.write(f"**Resume Missing Skills:** {reports['Report_B_Summary']['Total_Unmatched']}")

            st.divider()
            st.write("### 💬 Chat Interview Evaluation")
            st.dataframe(pd.DataFrame(reports["Report_B_Summary"]["Interview_Grades"]))

            st.write("### Interview Transcript")
            for skill, answer in reports["Report_B_Summary"]["Interview_Transcript"].items():
                st.write(f"**Q: Experience with {skill}?**")
                st.write(f"> {answer}")

        with tab3:
            if reports["Report_C_Training_Plan"]:
                st.dataframe(pd.DataFrame(reports["Report_C_Training_Plan"]))
            else:
                st.success("Candidate matches all skills! No training required.")

        st.divider()
        st.subheader("📧 Share Reports with HR")

        report_json_string = json.dumps(reports, indent=4)
        filename = f"Candidate_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        st.download_button(
            label="📥 Download HR Report (JSON)",
            data=report_json_string,
            file_name=filename,
            mime="application/json"
        )

        st.info(
            "Since this is hosted on Streamlit Cloud, click the button above to securely download the report to your local machine."
        )

else:
    if email_input or pass_input:
        st.sidebar.error("Invalid credentials.")
    st.info("👈 Please login from the sidebar to continue.")
