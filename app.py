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

# -------------------------
# Sidebar: Login + Job Pick
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

    # Assumes JOB_DESCRIPTION is:
    # ["", "valid jd 1", "valid jd 2"]
    selected_job_description = JOB_DESCRIPTION[job_choice]

    # Session state initialization
    if "job_choice" not in st.session_state:
        st.session_state.job_choice = job_choice

    if "job_description_text" not in st.session_state:
        st.session_state.job_description_text = selected_job_description

    if "resume_text" not in st.session_state:
        st.session_state.resume_text = RESUME_TEXT

    if "final_reports" not in st.session_state:
        st.session_state.final_reports = None

    # If user changes sidebar job choice, update JD text
    if st.session_state.job_choice != job_choice:
        st.session_state.job_choice = job_choice
        st.session_state.job_description_text = JOB_DESCRIPTION[job_choice]

    st.write("### Review / Edit Input Data")
    col1, col2 = st.columns(2)

    with col1:
        job_description_text = st.text_area(
            "Job Description",
            value=st.session_state.job_description_text,
            height=150,
            key="job_description_editor"
        )
        st.session_state.job_description_text = job_description_text

    with col2:
        resume_text = st.text_area(
            "Candidate Resume (You may CTRL-A and paste your own text resume)",
            value=st.session_state.resume_text,
            height=150,
            key="resume_editor"
        )
        st.session_state.resume_text = resume_text

    if st.button("Start AI Interview Process"):
        current_job_description = st.session_state.job_description_text.strip()
        current_resume_text = st.session_state.resume_text.strip()

        if not current_job_description:
            st.error("Please choose job 1 or 2, or enter a valid job description.")
        elif not current_resume_text:
            st.error("Please paste or enter a resume before starting.")
        else:
            with st.spinner("Analyzing JD and Resume..."):
                jd_skills = extract_jd_skills(current_job_description)
                resume_skills = extract_resume_skills(current_resume_text)

                analysis = analyze_and_score(jd_skills, resume_skills)
                interview_skills = get_top_5_interview_skills(jd_skills)

            st.success(f"Analysis Complete! Fit Score: {analysis['score_percentage']}%")
            st.write("### 🎙️ Voice Interview Starting...")

            transcript = conduct_voice_interview(interview_skills)

            with st.spinner("Grading interview answers and generating reports..."):
                grades = evaluate_interview_answers(transcript)
                training = generate_training_plan(analysis["unmatched"])

                st.session_state.final_reports = compile_all_reports(
                    analysis,
                    training,
                    transcript,
                    grades
                )

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
            st.write("### 🎙️ Voice Interview Evaluation")
            st.dataframe(pd.DataFrame(reports["Report_B_Summary"]["Interview_Grades"]))

            st.write("### Raw Transcript")
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
