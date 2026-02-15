#!/usr/bin/env python
"""Test script to debug AI Service initialization"""

import os
from dotenv import load_dotenv

print("=" * 60)
print("STEP 1: Before load_dotenv()")
print(f"GEMINI_API_KEY from os.environ: {os.environ.get('GEMINI_API_KEY', 'NOT SET')}")
print(f"GEMINI_API_KEY from os.getenv: {os.getenv('GEMINI_API_KEY', 'NOT SET')}")

print("\n" + "=" * 60)
print("STEP 2: Loading .env file")
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
print(f".env path: {dotenv_path}")
print(f".env exists: {os.path.exists(dotenv_path)}")
load_dotenv(dotenv_path, verbose=True, override=True)

print("\n" + "=" * 60)
print("STEP 3: After load_dotenv()")
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print(f"GEMINI_API_KEY: {gemini_key[:20]}... ({len(gemini_key)} chars)")
else:
    print("GEMINI_API_KEY: NOT SET")

print("\n" + "=" * 60)
print("STEP 4: Importing AIService")
from utils.ai_service import AIService

print("\n" + "=" * 60)
print("STEP 5: Creating AIService instance")
service = AIService()

print("\n" + "=" * 60)
print(f"STEP 6: Result - AI Service enabled: {service.enabled}")
print("=" * 60)
