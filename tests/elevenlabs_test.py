import os
import requests

# Load from your .env (optional)
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

assert API_KEY, "❌ ELEVENLABS_API_KEY not set"
assert VOICE_ID, "❌ ELEVENLABS_VOICE_ID not set"

print(f"🔑 Using API Key: {API_KEY[:6]}... (hidden)")
print(f"🎙️ Using Voice ID: {VOICE_ID}")
print(f"🧠 Using Model: {MODEL_ID}")

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}
data = {
    "text": "Hello! This is a test message from ElevenLabs.",
    "model_id": MODEL_ID,
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.7
    }
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    with open("test_output.mp3", "wb") as f:
        f.write(response.content)
    print("✅ Success! Saved audio as test_output.mp3")
else:
    print(f"❌ Error {response.status_code}: {response.text}")