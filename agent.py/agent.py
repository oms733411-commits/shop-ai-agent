import json
import os
import urllib.request
import urllib.error
from pathlib import Path


# Get Gemini API key from GitHub Actions Secret
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")


# Read the shop information
shop_info = Path("shop.yaml").read_text(encoding="utf-8")


# AI instructions
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
- Do NOT claim something is available unless supported by the shop information.
- Keep the content natural and suitable for Instagram.

Return exactly these sections:

POST IDEA:
CAPTION:
HASHTAGS:
CALL TO ACTION:
"""


# Gemini API request
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


# Send request to Gemini
try:
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

except urllib.error.HTTPError as error:
    body = error.read().decode(
        "utf-8",
        errors="replace"
    )

    print("Gemini API error:")
    print(body)

    raise


# Extract AI response
text = result["candidates"][0]["content"]["parts"][0]["text"]


# Show result in GitHub Actions
print()
print("=" * 60)
print("🤖 GHAR TAK — AI CONTENT ENGINE")
print("=" * 60)
print()
print(text)
print()
print("✅ AI content generation successful.")
