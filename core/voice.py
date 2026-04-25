"""
core/voice.py

NOTE:
This module originally supported voice-based interview interaction.
For now, it has been temporarily converted into a chat-based interview
module for better stability in both local and cloud deployments.

The file name remains `voice.py` so that the rest of the application
does not need to change its imports.
"""

import streamlit as st


def conduct_voice_interview(skills_to_test):
    """
    Temporary chat-based replacement for the voice interview flow.

    Displays interview questions and captures candidate responses as typed input.

    Args:
        skills_to_test (list): Skills selected for interview questioning

    Returns:
        dict | None: A transcript dictionary after submission, otherwise None
    """

    if "interview_submitted" not in st.session_state:
        st.session_state.interview_submitted = False

    if "interview_transcript" not in st.session_state:
        st.session_state.interview_transcript = {}

    st.write("### 💬 AI Chat Interview")
    st.info(
        "Voice mode is temporarily disabled. "
        "Please answer the following interview questions by typing your responses below."
    )

    if st.session_state.interview_submitted:
        for i, skill in enumerate(skills_to_test, start=1):
            question = f"Could you please explain your experience with {skill}?"
            st.write(f"**AI Question {i}:** {question}")
            st.text_area(
                label=f"Your answer for {skill}",
                value=st.session_state.interview_transcript.get(skill, ""),
                height=120,
                key=f"submitted_interview_answer_{i}_{skill}",
                disabled=True
            )

        st.success("Interview answers submitted successfully.")
        return st.session_state.interview_transcript

    with st.form("chat_interview_form"):
        current_transcript = {}

        for i, skill in enumerate(skills_to_test, start=1):
            question = f"Could you please explain your experience with {skill}?"
            st.write(f"**AI Question {i}:** {question}")

            answer = st.text_area(
                label=f"Your answer for {skill}",
                key=f"interview_answer_{i}_{skill}",
                height=120,
                placeholder=f"Type your experience with {skill} here..."
            )

            current_transcript[skill] = answer.strip() if answer else ""

        submitted = st.form_submit_button("✅ Submit Interview Answers")

        if submitted:
            for skill in current_transcript:
                if not current_transcript[skill]:
                    current_transcript[skill] = "No response provided"

            st.session_state.interview_transcript = current_transcript
            st.session_state.interview_submitted = True
            st.success("Interview answers submitted successfully.")
            return st.session_state.interview_transcript

    st.warning("Please answer the questions above and click 'Submit Interview Answers' to continue.")
    return None
