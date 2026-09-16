import json
import os
import urllib.request
import urllib.error
from pathlib import Path

print("🚀 AGENT STARTED")

# Check API key
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY is missing")

print("🔐 Gemini API key detected")

# Check shop file
shop_file = Path("shop.yaml")

if not shop_file.exists():
    raise RuntimeError("❌ shop.yaml was not found")

shop_info = shop_file.read_text(encoding="utf-8")

print("📄 shop.yaml loaded")
print("📏 Shop information length:", len(shop_info))

prompt = f"""
You are the AI marketing assistant for a local Indian grocery shop.

SHOP INFORMATION:
{shop_info}

Create ONE Instagram post for today.

Requirements:
- Language: Hindi
- Audience: local customers in Jamshedpur
- Tone: friendly, local, trustworthy and energetic
- Goal: increase local awareness, enquiries and shop visits
- Focus on grocery/supermarket products, flour milling, edible oil,
  masala and spices.
- Do NOT invent prices.
- Do NOT invent offers.
- Do NOT invent products.
- Do NOT create fake reviews.

Return exactly:

POST IDEA:
CAPTION:
HASHTAGS:
CALL TO ACTION:
"""

print("🧠 Sending request to Gemini...")

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": prompt
                }
            ]
        }
    ],
    "generationConfig": {
        "maxOutputTokens": 800
    }
}

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash:generateContent"
)

request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    },
    method="POST"
)

try:
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read().decode("utf-8")

    print("✅ Gemini responded")
    print("📦 Response received")
    
    result = json.loads(raw)

except urllib.error.HTTPError as error:
    print("❌ Gemini HTTP ERROR:", error.code)
    print(error.read().decode("utf-8", errors="replace"))
    raise

except Exception as error:
    print("❌ Gemini connection error:", repr(error))
    raise

print()
print("=" * 60)
print("🤖 GHAR TAK — AI CONTENT ENGINE")
print("=" * 60)

try:
    text = result["candidates"][0]["content"]["parts"][0]["text"]
    print(text)

except Exception:
    print("⚠️ Could not extract normal Gemini text.")
    print("Full response:")
    print(json.dumps(result, indent=2))

print()
print("✅ AGENT FINISHED")
