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
# 3. AI PROMPT
# ============================================================

prompt = f"""
You are the official Instagram content writer for Ghar Tak.

SHOP INFORMATION:
{shop_info}

Create ONE Instagram post for the shop.

The target audience is local customers in Jamshedpur.

Write natural, attractive Hindi suitable for Instagram.

IMPORTANT:
- Actually write the post.
- Do NOT explain your instructions.
- Do NOT discuss safety.
- Do NOT repeat the rules.
- Do NOT ask questions about the format.
- Do NOT say "format matched".
- Do NOT describe what you are doing.

Use EXACTLY this structure:

POST IDEA:
[one short idea]

CAPTION:
[short natural Hindi Instagram caption]

HASHTAGS:
[8-10 relevant hashtags]

CALL TO ACTION:
[one short Hindi call to action]

CONTENT RULES:

- Friendly, local, trustworthy and energetic tone.
- Promote genuine local awareness and shop visits.
- You may mention the shop's real specialties.
- You may mention flour milling, edible oil, masala, spices and grocery products when relevant.
- Never invent prices.
- Never invent discounts.
- Never invent offers.
- Never invent products.
- Never invent delivery service.
- Never invent opening hours.
- Never invent phone numbers.
- Never invent reviews.
- Never claim the shop is the cheapest or number one.
- Never make unsupported claims.
- Do not use fake urgency.
- Do not use spam.
- Do not encourage fake engagement.

Keep the caption concise.

OUTPUT ONLY THE FOUR SECTIONS.
"""


# ============================================================
# 4. GEMINI API
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
            "maxOutputTokens": 1400
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
# 5. PRIMARY MODEL + RETRIES
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

        print(
            f"⏳ Waiting {wait_time} seconds before retry..."
        )

        time.sleep(wait_time)


# ============================================================
# 6. FALLBACK MODEL
# ============================================================

if result is None:

    fallback_model = "gemini-3.5-flash-lite"

    print()
    print("============================================")
    print("⚠️ PRIMARY MODEL UNAVAILABLE")
    print("============================================")
    print("🔄 Trying fallback:", fallback_model)

    for attempt in range(1, 3):

        result = call_gemini(
            fallback_model,
            attempt
        )

        if result is not None:
            break

        if attempt < 2:
            time.sleep(10)


# ============================================================
# 7. FINAL FAILURE
# ============================================================

if result is None:

    print()
    print("============================================")
    print("❌ GEMINI REQUEST FAILED")
    print("============================================")

    raise SystemExit(1)


# ============================================================
# 8. EXTRACT RESPONSE
# ============================================================

try:

    text = (
        result["candidates"][0]
        ["content"]
        ["parts"][0]
        ["text"]
        .strip()
    )

except Exception:

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
# 9. CLEAN GEMINI RESPONSE
# ============================================================

# Remove markdown code fences if Gemini adds them.

text = text.replace("```text", "")
text = text.replace("```", "")
text = text.strip()


# ============================================================
# 10. AUTOMATIC FORMAT REPAIR
# ============================================================

if "POST IDEA:" not in text:
    text = "POST IDEA:\nआज के लिए Ghar Tak की स्थानीय किराना पोस्ट\n\n" + text


if "CAPTION:" not in text:

    parts = text.split("POST IDEA:", 1)

    if len(parts) == 2:

        idea = parts[1].strip()

        text = (
            "POST IDEA:\n"
            + idea
            + "\n\n"
            "CAPTION:\n"
            + idea
        )


if "HASHTAGS:" not in text:

    text += (
        "\n\n"
        "HASHTAGS:\n"
        "#GharTak #Jamshedpur #JamshedpurShopping "
        "#Grocery #Jharkhand #GroceryShopping"
    )


if "CALL TO ACTION:" not in text:

    text += (
        "\n\n"
        "CALL TO ACTION:\n"
        "आज ही Ghar Tak पर अपनी किराना जरूरतों के लिए पधारें।"
    )


# ============================================================
# 11. CLEAN EXCESSIVE BLANK LINES
# ============================================================

while "\n\n\n" in text:

    text = text.replace(
        "\n\n\n",
        "\n\n"
    )


# ============================================================
# 12. DISPLAY FINAL CONTENT
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
