import os
import time
import tempfile

import speech_recognition as sr
import streamlit as st
from gtts import gTTS


def get_deployed_on_cloud() -> bool:
    """
    Resolve deployment mode safely.
    Priority:
    1. Streamlit secrets
    2. Environment variable
    3. Default False
    """
    try:
        if "DEPLOYED_ON_CLOUD" in st.secrets:
            val = st.secrets["DEPLOYED_ON_CLOUD"]
            if isinstance(val, bool):
                return val
            return str(val).strip().lower() == "true"
    except Exception:
        pass

    env_val = os.environ.get("DEPLOYED_ON_CLOUD", "false")
    return str(env_val).strip().lower() == "true"


DEPLOYED_ON_CLOUD = get_deployed_on_cloud()


def speak(text: str):
    """
    Text-to-speech:
    - On cloud: render audio in browser without autoplay to avoid overlap
    - Local: play via mpg123 if available, else render in browser
    """
    try:
        t0 = time.time()
        st.caption("🔊 Generating voice...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            filename = tmp.name

        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(filename)

        t1 = time.time()
        st.caption(f"TTS generated in {t1 - t0:.2f}s")

        with open(filename, "rb") as f:
            audio_bytes = f.read()

        if DEPLOYED_ON_CLOUD:
            # Important: no autoplay on cloud, otherwise clips overlap
            st.audio(audio_bytes, format="audio/mp3")
        else:
            # Local blocking playback through system player
            exit_code = os.system(f'mpg123 -q "{filename}"')
            if exit_code != 0:
                st.warning("mpg123 not found. Falling back to browser audio player.")
                st.audio(audio_bytes, format="audio/mp3")

    except Exception as e:
        st.error(f"TTS Error: {e}")

    finally:
        try:
            if "filename" in locals() and os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass


def listen() -> str:
    """
    Speech-to-text:
    - On cloud: simulate a response because server-side mic access is not available
    - Local: use microphone + Google recognizer
    """
    if DEPLOYED_ON_CLOUD:
        st.info("🎙️ Web Demo Mode: Simulating candidate voice response...")
        return (
            "I have about 3 years of experience with this technology. "
            "I used it daily in my previous role to build scalable backend systems."
        )

    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.info("🎙️ Listening... Please speak now.")
            r.adjust_for_ambient_noise(source, duration=0.8)

            t0 = time.time()
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            t1 = time.time()

            text = r.recognize_google(audio)
            t2 = time.time()

            st.caption(f"Audio capture: {t1 - t0:.2f}s | STT: {t2 - t1:.2f}s")
            st.success(f"Candidate: {text}")
            return text

    except sr.WaitTimeoutError:
        return "No response (Timeout)"
    except sr.UnknownValueError:
        return "No response (Could not understand)"
    except Exception as e:
        return f"Error: {str(e)}"


def conduct_voice_interview(skills_to_test):
    """
    Ask questions for each target skill and capture responses.

    Cloud behavior:
    - display question text
    - do NOT auto-play audio, to avoid overlap
    - simulate candidate response

    Local behavior:
    - speak question aloud
    - capture spoken response from microphone
    """
    interview_transcript = {}

    intro = "Hello! I am the AI Hiring Assistant. Let's begin the interview."
    st.write(f"**AI:** {intro}")
    if not DEPLOYED_ON_CLOUD:
        speak(intro)

    for i, skill in enumerate(skills_to_test, start=1):
        question = f"Could you please explain your experience with {skill}?"
        st.write(f"**AI Question {i}:** {question}")

        if not DEPLOYED_ON_CLOUD:
            speak(question)

        t0 = time.time()
        answer = listen()
        t1 = time.time()

        st.caption(f"Response step for '{skill}' completed in {t1 - t0:.2f}s")
        interview_transcript[skill] = answer

    closing = "Thank you, the interview is now complete."
    st.write(f"**AI:** {closing}")
    if not DEPLOYED_ON_CLOUD:
        speak(closing)

    return interview_transcript
