import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path


print("============================================")
print("🤖 GHAR TAK AI AGENT")
print("============================================")
print("🚀 Agent started")


# ============================================================
# GEMINI API KEY
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ GEMINI_API_KEY is missing")
    raise SystemExit(1)

print("🔐 Gemini API key detected")


# ============================================================
# LOAD SHOP INFORMATION
# ============================================================

shop_path = Path("shop.yaml")

if not shop_path.exists():
    print("❌ shop.yaml was not found")
    raise SystemExit(1)

shop_info = shop_path.read_text(encoding="utf-8")

print("📄 shop.yaml loaded")
print("📏 Shop information length:", len(shop_info))


# ============================================================
# AI PROMPT
# ============================================================

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
- Make the content natural and useful
- Do NOT invent prices
- Do NOT invent offers
- Do NOT invent products
- Do NOT create fake reviews
- Do NOT make unsupported claims
- Do NOT use fake engagement tactics
- Do NOT encourage mass-following or spam

Return exactly:

POST IDEA:

CAPTION:

HASHTAGS:

CALL TO ACTION:
"""


# ============================================================
# GEMINI API FUNCTION
# ============================================================

def call_gemini(model_name, attempt_number):

    print()
    print("--------------------------------------------")
    print("🧠 Gemini model:", model_name)
    print("🔁 Attempt:", attempt_number)
    print("--------------------------------------------")

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
        f"v1beta/models/{model_name}:generateContent"
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

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            raw_response = response.read().decode("utf-8")

            result = json.loads(raw_response)

            print("✅ Gemini API responded")

            return result

    except urllib.error.HTTPError as error:

        print("❌ Gemini HTTP ERROR:", error.code)

        error_body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        print(error_body)

        return None

    except Exception as error:

        print("❌ Gemini connection error:")
        print(repr(error))

        return None


# ============================================================
# TRY PRIMARY MODEL
# ============================================================

result = None

primary_model = "gemini-3.6-flash"

print()
print("🚀 Trying primary model:", primary_model)


# Retry 3 times
for attempt in range(1, 4):

    result = call_gemini(
        primary_model,
        attempt
    )

    if result is not None:
        break

    if attempt < 3:

        wait_time = 10 * attempt

        print()
        print(
            f"⏳ Gemini unavailable. "
            f"Waiting {wait_time} seconds before retry..."
        )

        time.sleep(wait_time)


# ============================================================
# FALLBACK MODEL
# ============================================================

if result is None:

    fallback_model = "gemini-3.5-flash-lite"

    print()
    print("============================================")
    print("⚠️ PRIMARY MODEL UNAVAILABLE")
    print("============================================")
    print()
    print("🔄 Switching to fallback model:")
    print(f"   {fallback_model}")
    print()

    for attempt in range(1, 3):

        result = call_gemini(
            fallback_model,
            attempt
        )

        if result is not None:
            break

        if attempt < 2:

            print()
            print(
                "⏳ Fallback model unavailable."
            )

            time.sleep(10)


# ============================================================
# FINAL FAILURE CHECK
# ============================================================

if result is None:

    print()
    print("============================================")
    print("❌ GEMINI REQUEST FAILED")
    print("============================================")
    print()
    print(
        "Both Gemini models were temporarily unavailable."
    )
    print(
        "The agent will try again on the next scheduled run."
    )

    raise SystemExit(1)


# ============================================================
# EXTRACT GEMINI RESPONSE
# ============================================================

try:

    text = result["candidates"][0]["content"]["parts"][0]["text"]

except Exception:

    print()
    print("❌ Could not extract Gemini response")

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )

    raise SystemExit(1)


# ============================================================
# DISPLAY GENERATED CONTENT
# ============================================================

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
print()
print("🎯 Next step will be Instagram automation.")
print("============================================")
