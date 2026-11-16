from google import genai
from google.genai import types

def transcribe_audio(key, model, audio, mime):
    with genai.Client(api_key=key) as client:
        response = client.models.generate_content(
            model=model,
            contents=[types.Part.from_bytes(data=audio, mime_type=mime),
                      "Transcribe this meeting faithfully in its original language. "
                      "Do not summarize or invent speech. Mark unclear speech as [inaudible]. "
                      "Use speaker labels only when distinguishable."],
            config=types.GenerateContentConfig(temperature=0.1))
    if not response.text:
        raise ValueError("No transcript returned.")
    return response.text
