import json
import os
import urllib.request
import urllib.error
from pathlib import Path


print("============================================")
print("🤖 GHAR TAK AI AGENT")
print("============================================")
print("🚀 Agent started")


# Gemini API key
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ GEMINI_API_KEY is missing")
    raise SystemExit(1)

print("🔐 Gemini API key detected")


# Load shop information
shop_path = Path("shop.yaml")

if not shop_path.exists():
    print("❌ shop.yaml was not found")
    raise SystemExit(1)

shop_info = shop_path.read_text(encoding="utf-8")

print("📄 shop.yaml loaded")
print("📏 Shop information length:", len(shop_info))


# AI prompt
prompt = f"""
You are the AI marketing assistant for Ghar Tak.

SHOP INFORMATION:
{shop_info}

Create ONE Instagram marketing post for today.

Requirements:

- Language: Hindi
- Audience: local customers in Jamshedpur
- Tone: friendly, local, trustworthy and energetic
- Goal: increase local awareness, enquiries and shop visits
- Focus on grocery and supermarket products
- Highlight flour milling, edible oil, masala and spices when appropriate
- Do NOT invent prices
- Do NOT invent offers
- Do NOT invent products
- Do NOT create fake reviews
- Do NOT make unsupported claims
- Keep the content natural and useful

Return exactly:

POST IDEA:

CAPTION:

HASHTAGS:

CALL TO ACTION:
"""


# Gemini request
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


# CURRENT GEMINI MODEL
url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.6-flash:generateContent"
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


print("🧠 Sending request to Gemini 3.6 Flash...")


# Call Gemini
try:

    with urllib.request.urlopen(request, timeout=60) as response:

        raw_response = response.read().decode("utf-8")

        print("✅ Gemini API responded")

        result = json.loads(raw_response)


except urllib.error.HTTPError as error:

    print("❌ Gemini HTTP ERROR:", error.code)

    error_body = error.read().decode(
        "utf-8",
        errors="replace"
    )

    print(error_body)

    raise SystemExit(1)


except Exception as error:

    print("❌ Gemini connection error:")
    print(repr(error))

    raise SystemExit(1)


# Extract response
try:

    text = result["candidates"][0]["content"]["parts"][0]["text"]

except Exception:

    print("❌ Could not extract Gemini response")

    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ))

    raise SystemExit(1)


# Display result
print()
print("============================================")
print("📱 GHAR TAK — GENERATED INSTAGRAM CONTENT")
print("============================================")
print()
print(text)
print()
print("============================================")
print("✅ AI CONTENT GENERATION SUCCESSFUL")
print("============================================")
