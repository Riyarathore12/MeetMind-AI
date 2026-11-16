import os
import hashlib
from pathlib import Path
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from transcriber import transcribe_audio
from meeting_analyzer import analyze_meeting, ask_meeting
from report_generator import report_text, generate_pdf

st.set_page_config(page_title="MeetMind AI", page_icon="🎙️", layout="wide")
BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
st.html(BASE / "style.css")
try:
    key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    model = str(st.secrets.get("GEMINI_MODEL", "gemini-3.5-flash-lite"))
except FileNotFoundError:
    key = ""
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
key = key or os.getenv("GEMINI_API_KEY", "").strip()
with st.sidebar:
    st.title("◈ MeetMind AI")
    st.caption("DAY 02 / 30 • MEETING INTELLIGENCE")
    if key:
        st.success("Server API key configured")
    else:
        key = st.text_input("Gemini API key", type="password").strip()
    model = st.text_input("Gemini model", value=model)
    st.caption("Recordings and transcripts are sent to Google Gemini only when you request AI processing.")
    st.markdown("[Get a Gemini API key](https://aistudio.google.com/apikey)")
    st.divider()
    st.caption("Review AI-generated minutes before sharing.")

st.html("""<div class="hero"><div class="eyebrow">✦ AI MEETING INTELLIGENCE</div>
<h1>Turn conversations<br>into <span>action.</span></h1>
<p>Transcribe meetings, capture decisions and turn discussions into actionable tasks.</p>
<div class="tags">Audio transcription · Smart action items · Evidence-based insights</div></div>""")
title = st.text_input("Meeting title", "Project planning meeting")
mode = st.radio("Input source", ["Upload audio", "Record audio", "Paste transcript"], horizontal=True)
audio = None
transcript_input = ""
if mode == "Upload audio":
    audio = st.file_uploader("Upload meeting audio (maximum 15 MB)", type=["mp3","wav","m4a","ogg","flac"])
elif mode == "Record audio":
    audio = st.audio_input("Record a meeting")
else:
    transcript_input = st.text_area("Meeting transcript", height=240)
    if st.button("Load sample transcript"):
        st.session_state["sample"] = True
    if st.session_state.get("sample") and not transcript_input:
        transcript_input = (BASE / "sample_meeting.txt").read_text(encoding="utf-8")
        st.info("Sample transcript loaded.")
        st.text(transcript_input)
consent = st.checkbox("I have permission from participants to process this meeting with Gemini.")
if "result" not in st.session_state:
    st.session_state.result = None
def safe_error(error):
    return str(error).replace(key, "[REDACTED]") if key else str(error)
if st.button("✦ Analyze meeting", type="primary", disabled=not consent, use_container_width=True):
    st.session_state.result = None
    try:
        if not key:
            raise ValueError("Configure a valid Gemini API key in the sidebar or .env.")
        with st.spinner("Transcribing and extracting meeting intelligence..."):
            if mode == "Paste transcript":
                transcript = transcript_input.strip()
            else:
                if audio is None:
                    raise ValueError("Please upload or record audio.")
                raw = audio.getvalue()
                if len(raw) > 15 * 1024 * 1024:
                    raise ValueError("Audio exceeds 15 MB. Split the recording into smaller parts.")
                ext = Path(audio.name).suffix.lower()
                mime = {".mp3":"audio/mpeg",".wav":"audio/wav",".m4a":"audio/mp4",
                        ".ogg":"audio/ogg",".flac":"audio/flac"}.get(ext, audio.type or "audio/wav")
                transcript = transcribe_audio(key, model, raw, mime)
            if not transcript:
                raise ValueError("No meeting transcript supplied.")
            data = analyze_meeting(key, model, transcript)
            st.session_state.result = (title, transcript, data)
    except Exception as error:
        st.error(safe_error(error))

if st.session_state.result:
    meeting_title, transcript, data = st.session_state.result
    actions = data.get("actions", [])
    decisions = data.get("decisions", [])
    st.subheader(meeting_title)
    a,b,c = st.columns(3)
    a.metric("Transcript words", len(transcript.split()))
    b.metric("Action items", len(actions))
    c.metric("Decisions", len(decisions))
    summary, tasks, text_tab, email, qa = st.tabs(["Overview","Action tracker","Transcript","Follow-up email","Ask meeting"])
    with summary:
        st.markdown("### Meeting summary")
        st.write(data.get("summary", ""))
        st.markdown("### Key decisions")
        for decision in decisions:
            st.write("• " + str(decision))
        st.markdown("### Open questions")
        for question in data.get("open_questions", []):
            st.write("• " + str(question))
    with tasks:
        if actions:
            df = pd.DataFrame(actions)
            df.insert(0, "Done", False)
            edited = st.data_editor(df, hide_index=True, use_container_width=True,
                                    key="tasks_" + hashlib.sha256(transcript.encode()).hexdigest())
            st.download_button("Download action items CSV", edited.to_csv(index=False), "action_items.csv", "text/csv")
        else:
            st.info("No action items identified.")
    with text_tab:
        search = st.text_input("Search transcript")
        if search:
            for line in transcript.splitlines():
                if search.lower() in line.lower():
                    st.write(line)
        st.text_area("Full transcript", transcript, height=350, disabled=True)
    with email:
        st.text_area("Review and copy email draft", data.get("follow_up_email", ""), height=280)
    with qa:
        question = st.text_input("Ask a question about this meeting")
        if st.button("Ask AI", disabled=not consent):
            if question.strip() and key:
                try:
                    with st.spinner("Searching transcript..."):
                        st.write(ask_meeting(key, model, transcript, question))
                except Exception as error:
                    st.error(safe_error(error))
    st.divider()
    st.caption("AI output may contain errors. Verify tasks, dates and evidence before use.")
    report = report_text(meeting_title, data, transcript)
    x,y = st.columns(2)
    x.download_button("↓ Download minutes TXT", report, "meeting_minutes.txt", "text/plain")
    try:
        y.download_button("↓ Download minutes PDF", generate_pdf(report), "meeting_minutes.pdf", "application/pdf")
    except Exception as error:
        y.warning("PDF export unavailable; use TXT for full Unicode text.")
st.html('<div class="footer">◈ MeetMind AI · Day 02 / 30 · Built with Python & Gemini</div>')
