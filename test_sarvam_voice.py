#!/usr/bin/env python3
"""
Test script for Sarvam AI Voice Pipeline implementation.

This script tests:
1. SarvamService initialization
2. Text-to-Speech (TTS) functionality
3. Speech-to-Text (STT) functionality
4. Language identification
5. Translation

Note: Requires SARVAM_API_KEY in .env file
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.sarvam_service import sarvam_service


async def test_tts():
    """Test Text-to-Speech functionality."""
    print("=" * 60)
    print("Testing Text-to-Speech (TTS) - Bulbul v1")
    print("=" * 60)

    test_texts = [
        ("Hello, this is a test message.", "en-IN", "Meera"),
        ("नमस्ते, यह एक परीक्षण संदेश है।", "hi-IN", "Meera"),
        ("मैं ठीक हूं, आप कैसे हैं?", "hi-IN", "Meera"),
    ]

    for text, lang, speaker in test_texts:
        try:
            print(f"\nText: {text}")
            print(f"Language: {lang}, Speaker: {speaker}")

            audio_bytes = await sarvam_service.text_to_speech(
                text=text,
                language_code=lang,
                speaker=speaker,
                model="bulbul:v1",
            )

            print(f"✓ TTS successful! Generated {len(audio_bytes)} bytes of audio")

            # Save to file for manual verification
            output_file = f"test_output_{lang}.wav"
            with open(output_file, "wb") as f:
                f.write(audio_bytes)
            print(f"  Saved to: {output_file}")

        except Exception as e:
            print(f"✗ TTS failed: {e}")


async def test_identify_language():
    """Test Language Identification."""
    print("\n" + "=" * 60)
    print("Testing Language Identification")
    print("=" * 60)

    test_texts = [
        "Hello, how are you?",
        "नमस्ते, आप कैसे हैं?",
        "હેલો, તમે કેમ છો?",
        "مرحبا، كيف حالك؟",
    ]

    for text in test_texts:
        try:
            print(f"\nText: {text}")
            result = await sarvam_service.identify_language(text=text)
            print(f"✓ Language: {result.get('language_code')}")
            print(f"  Script: {result.get('script')}")
        except Exception as e:
            print(f"✗ Language identification failed: {e}")


async def test_translation():
    """Test Text Translation."""
    print("\n" + "=" * 60)
    print("Testing Text Translation - Mayura v1")
    print("=" * 60)

    translations = [
        ("नमस्ते, मैं ठीक हूं", "auto", "en-IN"),
        ("Hello, I am fine", "en-IN", "hi-IN"),
        ("તમે કેમ છો?", "gu-IN", "en-IN"),
    ]

    for text, source, target in translations:
        try:
            print(f"\nSource: {text}")
            print(f"{source} → {target}")

            result = await sarvam_service.translate_text(
                text=text,
                source_language_code=source,
                target_language_code=target,
                model="mayura:v1",
            )

            print(f"✓ Translation: {result.get('translated_text')}")

        except Exception as e:
            print(f"✗ Translation failed: {e}")


async def test_stt_simulation():
    """Simulate STT (Speech-to-Text) test - requires actual audio file."""
    print("\n" + "=" * 60)
    print("Testing Speech-to-Text (STT) - Saarika v2")
    print("=" * 60)
    print("\nNote: This requires an actual audio file.")
    print("Create a test_audio.wav file and uncomment the code below to test.")

    # Uncomment to test with actual audio file:
    # audio_file_path = "test_audio.wav"
    # if os.path.exists(audio_file_path):
    #     try:
    #         with open(audio_file_path, "rb") as f:
    #             audio_data = f.read()
    #
    #         print(f"\nAudio file: {audio_file_path} ({len(audio_data)} bytes)")
    #
    #         result = await sarvam_service.speech_to_text(
    #             audio_data=audio_data,
    #             language_code="unknown",
    #             model="saarika:v2",
    #         )
    #
    #         print(f"✓ STT successful!")
    #         print(f"  Transcript: {result.get('transcript')}")
    #         print(f"  Language: {result.get('language_code')}")
    #         print(f"  Confidence: {result.get('confidence')}")
    #
    #     except Exception as e:
    #         print(f"✗ STT failed: {e}")
    # else:
    #     print(f"Audio file not found: {audio_file_path}")


async def test_service_availability():
    """Test if Sarvam service is properly initialized."""
    print("=" * 60)
    print("Testing Sarvam Service Availability")
    print("=" * 60)

    try:
        client = sarvam_service.client
        print(f"✓ SarvamAI client initialized successfully")
        print(f"  API Key: {'*' * 20}{sarvam_service.client.api_subscription_key[-10:] if sarvam_service.client.api_subscription_key else 'Not set'}")

        if not sarvam_service.client.api_subscription_key:
            print("\n⚠ WARNING: SARVAM_API_KEY not set in environment!")
            print("  Add your API key to the .env file:")
            print("  SARVAM_API_KEY=your_api_key_here")

    except Exception as e:
        print(f"✗ Service initialization failed: {e}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SARVAM AI VOICE PIPELINE TEST SUITE")
    print("=" * 60)

    # Test service initialization
    await test_service_availability()

    # Check if API key is set
    if not sarvam_service.client.api_subscription_key:
        print("\n⚠ Skipping tests - SARVAM_API_KEY not set")
        print("  Please set SARVAM_API_KEY in your .env file and run again.")
        return

    # Run tests
    await test_identify_language()
    await test_translation()
    await test_tts()
    await test_stt_simulation()

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
