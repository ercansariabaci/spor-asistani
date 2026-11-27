"""Gemini bağlantısını uygulamadan bağımsız test eder: python test_gemini.py"""
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
istemci = genai.Client(api_key=os.getenv("GEMINI_API_KEY"),
                       http_options=types.HttpOptions(timeout=30_000))

print("1) Kullanılabilir Flash modelleri:")
for m in istemci.models.list():
    if "flash" in m.name and "generateContent" in (m.supported_actions or []):
        print("   ", m.name)

model = os.getenv("GEMINI_MODEL") or input("\n2) Denenecek model adını yaz (models/ olmadan): ").strip()
print(f"\n3) {model} modeline kısa bir soru gönderiliyor...")
baslangic = time.time()
try:
    cevap = istemci.models.generate_content(model=model, contents="Sadece 'merhaba' yaz.")
    print(f"   ✅ Cevap ({time.time() - baslangic:.1f} sn): {cevap.text}")
except Exception as hata:
    print(f"   ❌ Hata ({time.time() - baslangic:.1f} sn): {hata}")
