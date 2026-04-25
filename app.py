import streamlit as st
import pandas as pd
from utils.mock_data import AUTH, JOB_DESCRIPTION, RESUME_TEXT
from core.skill_matcher import extract_jd_skills, extract_resume_skills, analyze_and_score, get_top_5_interview_skills
from core.voice import conduct_voice_interview
from core.reporter import generate_training_plan, evaluate_interview_answers, compile_all_reports
from utils.hr_notifier import share_with_hr

st.set_page_config(page_title="AI Hiring Agent", layout="wide")

st.title("🤖 AI Hiring Agent - Candidate Portal")

# Sidebar Auth
st.sidebar.header("Login")
email_input = st.sidebar.text_input("Email")
pass_input = st.sidebar.text_input("Password", type="password")

if email_input == AUTH["email"] and pass_input == AUTH["password"]:
    st.sidebar.success("Logged in successfully!")

    st.write("### Review Hardcoded Data (Hackathon)")
    col1, col2 = st.columns(2)
    with col1:
        st.text_area("Job Description", JOB_DESCRIPTION, height=150)
    with col2:
        st.text_area("Candidate Resume", RESUME_TEXT, height=150)

    if 'final_reports' not in st.session_state:
        st.session_state.final_reports = None

    if st.button("🚀 Start AI Interview Process"):
        with st.spinner("Analyzing JD and Resume..."):
            jd_skills = extract_jd_skills(JOB_DESCRIPTION)
            resume_skills = extract_resume_skills(RESUME_TEXT)

            # 1. Scoring & Matching
            analysis = analyze_and_score(jd_skills, resume_skills)

            # 2. Top Skills for Interview
            interview_skills = get_top_5_interview_skills(jd_skills)

        st.success(f"Analysis Complete! Fit Score: {analysis['score_percentage']}%")
        st.write("### 🎙️ Voice Interview Starting...")

         # 3. Voice Interview
        transcript = conduct_voice_interview(interview_skills)

        # 4. Evaluate Answers & Generate Reports
        with st.spinner("Grading interview answers and generating reports..."):
            # Grade the actual voice answers!
            grades = evaluate_interview_answers(transcript)

            # Generate the training plan for missing skills
            training = generate_training_plan(analysis["unmatched"])

            # Compile everything
            st.session_state.final_reports = compile_all_reports(analysis, training, transcript, grades)

    # 5. Display Reports
    if st.session_state.final_reports:
        reports = st.session_state.final_reports

        st.divider()
        st.header("📊 Evaluation Reports")

        tab1, tab2, tab3 = st.tabs(["Report A: Skills Match", "Report B: Summary & Score", "Report C: Training Plan"])

        with tab1:
            st.dataframe(pd.DataFrame(reports["Report_A_Skill_Match"]))

        with tab2:
            st.metric("Initial Resume Fit Score", f"{reports['Report_B_Summary']['Resume_Fit_Score']}%")
            st.write(f"**Resume Matched Skills:** {reports['Report_B_Summary']['Total_Matched']}")
            st.write(f"**Resume Missing Skills:** {reports['Report_B_Summary']['Total_Unmatched']}")

            st.divider()
            st.write("### 🎙️ Voice Interview Evaluation")

            # Display the AI's grading of the audio answers
            st.dataframe(pd.DataFrame(reports['Report_B_Summary']['Interview_Grades']))

            st.write("### Raw Transcript")
            for skill, answer in reports['Report_B_Summary']['Interview_Transcript'].items():
                st.write(f"**Q: Experience with {skill}?**")
                st.write(f"> {answer}")

        with tab3:
            if reports["Report_C_Training_Plan"]:
                st.dataframe(pd.DataFrame(reports["Report_C_Training_Plan"]))
            else:
                st.success("Candidate matches all skills! No training required.")

        st.divider()
        st.subheader("📧 Share Reports with HR")

        # Convert the dictionary to a formatted JSON string
        import json
        from datetime import datetime
        report_json_string = json.dumps(reports, indent=4)
        filename = f"Candidate_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Streamlit Native Download Button
        st.download_button(
            label="📥 Download HR Report (JSON)",
            data=report_json_string,
            file_name=filename,
            mime="application/json"
        )

        st.info("Since this is hosted on Streamlit Cloud, click the button above to securely download the report to your local machine.")

else:
    if email_input or pass_input:
        st.sidebar.error("Invalid credentials.")
    st.info("👈 Please login from the sidebar to continue.")
