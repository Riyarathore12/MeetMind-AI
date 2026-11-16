# MeetMind AI — Day 02/30
Meeting intelligence with audio transcription, summaries, decisions, evidence-backed tasks, transcript search, follow-up drafts and Q&A.

## Windows quick start
Install Python 3.12 if needed. Extract the ZIP and double-click `run.bat`, or run:
```
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Enter a valid Gemini API key in the sidebar, or copy `.env.example` to `.env` and configure it.
The default model is the model used in the previous project; change it if your key does not support it.
Use the sample transcript for a quick test. Audio is transcribed by Gemini (not local Whisper) to keep deployment lightweight. No FFmpeg required.
## Deploy
Push files to GitHub (never .env or secrets). On Streamlit Community Cloud choose app.py, Python 3.12, and configure GEMINI_API_KEY and GEMINI_MODEL in Secrets. A shared key consumes your quota; prefer visitor keys for public demos.
## Limitations
Requires a working Gemini key and audio-capable model. 15 MB audio limit. Speaker labels and extracted tasks may be inaccurate. PDF uses default Latin fonts; TXT preserves Unicode. Task edits are exported in CSV; meeting minutes use original AI analysis. No live meeting bot or persistent storage. Obtain participant consent before processing.
