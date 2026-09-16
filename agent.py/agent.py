from pathlib import Path

shop = Path("shop.yaml").read_text(encoding="utf-8")

print("🤖 Ghar Tak Shop AI Agent")
print("☁️ Cloud execution: OK")
print("💰 Paid services: OFF")
print("🔐 Secrets: NOT stored in code")
print()
print("=== SHOP BRAIN ===")
print(shop)
print()
print("✅ Agent successfully loaded shop information.")
