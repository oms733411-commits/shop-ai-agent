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
# 1. GEMINI API KEY
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ GEMINI_API_KEY is missing")
    raise SystemExit(1)

print("🔐 Gemini API key detected")


# ============================================================
# 2. LOAD SHOP INFORMATION
# ============================================================

shop_path = Path("shop.yaml")

if not shop_path.exists():
    print("❌ shop.yaml was not found")
    raise SystemExit(1)

shop_info = shop_path.read_text(encoding="utf-8")

print("📄 shop.yaml loaded")
print("📏 Shop information length:", len(shop_info))


# ============================================================
# 3. STRICT AI PROMPT
# ============================================================

prompt = f"""
You are the official Instagram content writer for the shop described below.

SHOP INFORMATION:
{shop_info}

Your task is to create ONE realistic Instagram post for this shop.

IMPORTANT:
You must actually WRITE THE POST.
Do not discuss the instructions.
Do not answer the requirements as questions.
Do not explain what you are doing.
Do not repeat the shop rules.
Do not say whether something is safe.
Do not say whether the output format was matched.

The final response MUST contain only these four sections:

POST IDEA:
[one short post idea]

CAPTION:
[a natural Hindi Instagram caption]

HASHTAGS:
[8 to 12 relevant hashtags]

CALL TO ACTION:
[one short Hindi call to action]

CONTENT RULES:

1. Write naturally for local customers in Jamshedpur.
2. Language should primarily be Hindi.
3. The tone should be friendly, local, trustworthy and energetic.
4. The purpose is to create local awareness and encourage genuine shop enquiries/visits.
5. You may mention the shop name and location from SHOP INFORMATION.
6. You may mention flour milling, edible oil, masala, spices and grocery products ONLY when supported by SHOP INFORMATION.
7. NEVER invent a price.
8. NEVER invent a discount.
9. NEVER invent an offer.
10. NEVER invent a product that is not supported by SHOP INFORMATION.
11. NEVER invent delivery availability.
12. NEVER invent opening/closing hours.
13. NEVER invent phone numbers or contact details.
14. NEVER create fake reviews or testimonials.
15. NEVER claim "cheapest", "number 1", "best in Jamshedpur" or similar unsupported claims.
16. Do not use fake urgency.
17. Do not use spammy engagement bait.
18. Keep the caption concise and suitable for Instagram.
19. Make the post useful or interesting rather than sounding like a generic advertisement.
20. Hashtags should be relevant to Jamshedpur, grocery shopping and the actual shop/products.

Now write the final Instagram post.

Remember:
OUTPUT ONLY THE FOUR REQUIRED SECTIONS.
"""


# ============================================================
# 4. GEMINI REQUEST
# ============================================================

def call_gemini(model_name, attempt):

    print()
    print("--------------------------------------------")
    print("🧠 Gemini model:", model_name)
    print("🔁 Attempt:", attempt)
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
            "maxOutputTokens": 1000
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
# 5. GET GEMINI RESPONSE WITH RETRIES
# ============================================================

result = None

primary_model = "gemini-3.6-flash"

print()
print("🚀 Trying primary model:", primary_model)

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
            f"⏳ Gemini temporarily unavailable."
            f" Waiting {wait_time} seconds..."
        )

        time.sleep(wait_time)


# ============================================================
# 6. FALLBACK MODEL
# ============================================================

if result is None:

    fallback_model = "gemini-3.5-flash-lite"

    print()
    print("============================================")
    print("⚠️ PRIMARY MODEL FAILED")
    print("============================================")
    print("🔄 Trying fallback model:", fallback_model)

    for attempt in range(1, 3):

        result = call_gemini(
            fallback_model,
            attempt
        )

        if result is not None:
            break

        if attempt < 2:

            print("⏳ Waiting 10 seconds...")
            time.sleep(10)


# ============================================================
# 7. STOP IF BOTH MODELS FAILED
# ============================================================

if result is None:

    print()
    print("============================================")
    print("❌ GEMINI REQUEST FAILED")
    print("============================================")
    print()
    print("No content was generated.")
    print("The next scheduled run will try again.")

    raise SystemExit(1)


# ============================================================
# 8. EXTRACT TEXT
# ============================================================

try:

    text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

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
# 9. VALIDATE OUTPUT
# ============================================================

required_sections = [
    "POST IDEA:",
    "CAPTION:",
    "HASHTAGS:",
    "CALL TO ACTION:"
]

missing_sections = [
    section
    for section in required_sections
    if section not in text
]


if missing_sections:

    print()
    print("⚠️ Gemini returned an unexpected format.")
    print("Missing sections:")

    for section in missing_sections:
        print(" -", section)

    print()
    print("Raw Gemini response:")
    print("--------------------------------------------")
    print(text)
    print("--------------------------------------------")

    raise SystemExit(1)


# ============================================================
# 10. DISPLAY FINAL INSTAGRAM CONTENT
# ============================================================

print()
print("============================================")
print("📱 GHAR TAK — INSTAGRAM CONTENT")
print("============================================")
print()
print(text)
print()
print("============================================")
print("✅ CONTENT GENERATION SUCCESSFUL")
print("============================================")
print()
print("☁️ Cloud agent test completed.")
print("📌 Instagram is NOT connected yet.")
print("============================================")
