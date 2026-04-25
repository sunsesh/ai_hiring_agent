import speech_recognition as sr
import streamlit as st
from gtts import gTTS
import os
import time

# 🚨 SET THIS TO 'True' BEFORE UPLOADING TO GITHUB / STREAMLIT CLOUD 🚨
DEPLOYED_ON_CLOUD = True

def speak(text):
    """Smart TTS: Plays in browser if on Cloud, uses mpg123 if local"""
    try:
        # 1. Generate Speech
        tts = gTTS(text=text, lang='en', slow=False)
        filename = "temp_voice.mp3"
        tts.save(filename)

        # 2. Play Audio
        if DEPLOYED_ON_CLOUD:
            # Send audio file directly to the user's web browser!
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            time.sleep(4) # Pause so the audio has time to play
        else:
            # Play locally via system player
            os.system(f"mpg123 -q {filename}")

        # 3. Cleanup
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        st.error(f"TTS Error: {e}")

def listen():
    """Smart STT: Simulates input on web, uses real mic locally"""
    if DEPLOYED_ON_CLOUD:
        # Cloud servers have no mic! We simulate an answer so the app doesn't crash for judges.
        st.info("🎙️ (Web Demo Mode) Simulating candidate voice response...")
        time.sleep(3)
        return "I have about 3 years of experience with this technology. I used it daily in my previous role to build scalable backend systems."

    # --- LOCAL MIC LOGIC ---
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Please speak now.")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            text = r.recognize_google(audio)
            st.success(f"Candidate: {text}")
            return text
        except sr.WaitTimeoutError:
            return "No response (Timeout)"
        except sr.UnknownValueError:
            return "No response (Could not understand)"
        except Exception as e:
            return f"Error: {str(e)}"

def conduct_voice_interview(skills_to_test):
    """Loops through skills and asks candidate about them."""
    interview_transcript = {}
    speak("Hello! I am the AI Hiring Assistant. Let's begin the interview.")

    for skill in skills_to_test:
        question = f"Could you please explain your experience with {skill}?"
        st.write(f"**AI:** {question}")
        speak(question)

        answer = listen()
        interview_transcript[skill] = answer

    speak("Thank you, the interview is now complete.")
    return interview_transcript
