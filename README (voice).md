# 🤖 AI Hiring Agent - Candidate Screening Portal

An intelligent, fully automated AI hiring assistant built for efficient technical screening. Powered by **Groq** (Llama-3.3-70B) and **Streamlit**, this agent extracts skills from a candidate's resume, matches them against a job description, conducts a dynamic voice-based interview, and generates structured evaluation reports for HR.

---

## ✨ Features
1. **Automated Skill Matching:** Parses Resume and Job Description (JD) to calculate a weighted fit score.
2. **Dynamic Voice Interview:** Uses Text-to-Speech (gTTS) and Speech-to-Text (`SpeechRecognition`) to ask candidates to explain their experience with their top 5 technical and soft skills.
3. **AI Interview Grading:** The LLM actively grades the audio transcript to catch padded resumes.
4. **Custom Training Plans:** Automatically generates a time-estimated training plan for the skills the candidate lacks.
5. **HR Reporting:** Securely compiles and exports a comprehensive evaluation JSON for HR review.

---

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **LLM Engine:** Groq API (`llama-3.3-70b-versatile`)
* **Voice / Audio:** `SpeechRecognition`, `gTTS`, `mpg123`
* **Data Handling:** Python, JSON, Pandas

---

## Setup & Installation (Local Development)

Because this app uses hardware audio drivers for the voice interview, you **must** install system-level audio dependencies before installing the Python packages.

### Step 1: Check your exact Python Version
Open your terminal and run:
```bash
python3 --version
```
*(Take note of the version number, e.g., Python 3.11 or 3.12. You will need this for the next step!)*

### Step 2: Install System Audio Drivers (Linux / Ubuntu / Mint)
You need the C-headers for your specific Python version, plus PortAudio (for microphone input) and mpg123 (for safe audio playback).
Replace `3.X` below with your version from Step 1 (e.g., `3.11`):
```bash
sudo apt-get update
sudo apt-get install python3.X-dev portaudio19-dev mpg123
```
*(Mac Users: run `brew install portaudio` | Windows Users: run `pip install pipwin` then `pipwin install pyaudio`)*

### Step 3: Create a Virtual Environment
It is highly recommended to run this in an isolated environment.
```bash
git clone https://github.com/YOUR_USERNAME/ai-hiring-agent.git
cd ai-hiring-agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 4: Install Python Dependencies
Now that your system headers are installed, `pyaudio` will compile successfully!
```bash
pip install -r requirements.txt
```

### Step 5: Configure your Groq API Key
Create a file named `.env` in the root directory and add your Groq API key:
```text
GROQ_API_KEY=gsk_your_api_key_here
```
*(Note: Do not upload your `.env` file to GitHub! It is safely ignored via `.gitignore`)*

---

## 💻 Running the App

To start the local Streamlit server, run:
```bash
streamlit run app.py
```
**Default Test Credentials:**
* **Email:** candidate@email.com
* **Password:** password123

---

## ☁️ Cloud Deployment (Streamlit Community Cloud)

This app is configured to be "Cloud Smart." Because cloud servers do not have physical microphones or speakers, the app includes a fallback mode to prevent crashes when deployed to the web.

### How to Deploy
1. **System Packages:** Ensure the `packages.txt` file is present in your repository. This tells Streamlit Cloud to automatically install the required Linux audio dependencies (`portaudio19-dev`, `mpg123`).
2. **Enable Cloud Mode:** Open `core/voice.py` and set the toggle variable:
   ```python
   DEPLOYED_ON_CLOUD = True
   ```
   *When True, the app routes audio through the web browser (`st.audio`) and safely simulates microphone input for web users.*
3. **Set Secrets:** Deploy on Streamlit Cloud, go to **Settings > Secrets**, and add your API key:
   ```toml
   GROQ_API_KEY="gsk_your_api_key_here"
   ```

---

## Project Structure

```text
ai-hiring-agent/
│
├── README.md               # Setup Instructions
├── .env                    # Groq API Key (Git-ignored)
├── .gitignore              # Ignored files
├── requirements.txt        # Python dependencies
├── packages.txt            # System dependencies (for Streamlit Cloud)
├── app.py                  # Main Streamlit Frontend
│
├── core/                   # Core Business Logic
│   ├── __init__.py
│   ├── llm_engine.py       # Groq API connection and JSON formatting
│   ├── skill_matcher.py    # JD vs Resume weighted scoring algorithm
│   ├── voice.py            # STT / TTS and Cloud Audio Routing
│   └── reporter.py         # AI Grading and Report Generation
│
└── utils/                  # Helper Utilities
    ├── __init__.py
    ├── mock_data.py        # Hackathon test data (JD, Resume)
    └── hr_notifier.py      # Local HR report saving simulation
```

---

## 🏆 Hackathon Context
This project was built as a rapid prototype over a hackathon weekend. Due to time constraints, the user database and JD/Resume inputs are currently mocked in `utils/mock_data.py`. For a full production rollout, the architecture would decouple the candidate-facing app from an internal HR dashboard, utilizing a cloud database (e.g., PostgreSQL) and PDF extraction tools.
