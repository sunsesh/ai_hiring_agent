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
    - On cloud: render audio in browser
    - Local: play via mpg123 if available, else render in browser
    """
    try:
        t0 = time.time()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            filename = tmp.name

        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(filename)

        t1 = time.time()
        st.caption(f"TTS generated in {t1 - t0:.2f}s")

        if DEPLOYED_ON_CLOUD:
            with open(filename, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        else:
            # Try local system playback first
            exit_code = os.system(f'mpg123 -q "{filename}"')
            if exit_code != 0:
                # Fallback to browser playback if mpg123 is unavailable
                with open(filename, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)

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
    """
    interview_transcript = {}

    speak("Hello! I am the AI Hiring Assistant. Let's begin the interview.")

    for i, skill in enumerate(skills_to_test, start=1):
        question = f"Could you please explain your experience with {skill}?"
        st.write(f"**AI Question {i}:** {question}")

        speak(question)

        t0 = time.time()
        answer = listen()
        t1 = time.time()

        st.caption(f"Total response step for '{skill}': {t1 - t0:.2f}s")
        interview_transcript[skill] = answer

    speak("Thank you, the interview is now complete.")
    return interview_transcript
