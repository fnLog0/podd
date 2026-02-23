import base64
import io
from typing import Optional
from sarvamai import SarvamAI
from src.config import settings


class SarvamService:
    def __init__(self):
        self.client = SarvamAI(api_subscription_key=settings.SARVAM_API_KEY)

    async def speech_to_text(
        self,
        audio_data: bytes,
        language_code: str = "unknown",
        model: str = "saarika:v2",
        with_translation: bool = False,
    ) -> dict:
        """
        Convert speech to text using Sarvam AI STT.

        Args:
            audio_data: Raw audio bytes
            language_code: Language code (e.g., hi-IN, en-IN, unknown for auto-detect)
            model: STT model to use (saarika:v1, saarika:v2)
            with_translation: If True, translates transcript to English

        Returns:
            Dictionary containing transcript and metadata
        """
        try:
            from sarvamai.core import File as SarvamFile

            audio_file = SarvamFile(payload=audio_data)

            if with_translation:
                response = self.client.speech_to_text.translate(
                    file=audio_file,
                    model=model,
                )
                return {
                    "transcript": response.get("transcript", ""),
                    "translated_text": response.get("translated_text", ""),
                    "language_code": response.get("language_code", "unknown"),
                    "confidence": response.get("confidence", 0.0),
                }
            else:
                response = self.client.speech_to_text.transcribe(
                    file=audio_file,
                    model=model,
                    language_code=language_code,
                )
                return {
                    "transcript": response.get("transcript", ""),
                    "language_code": response.get("language_code", language_code),
                    "confidence": response.get("confidence", 0.0),
                }
        except Exception as e:
            raise ValueError(f"Speech-to-text failed: {str(e)}")

    async def text_to_speech(
        self,
        text: str,
        language_code: str = "hi-IN",
        speaker: str = "Meera",
        model: str = "bulbul:v1",
        pitch: float = 0.0,
        pace: float = 1.0,
        loudness: float = 1.0,
        sample_rate: int = 22050,
        enable_preprocessing: bool = False,
    ) -> bytes:
        """
        Convert text to speech using Sarvam AI TTS.

        Args:
            text: Text to convert to speech
            language_code: Target language code (e.g., hi-IN, en-IN)
            speaker: Speaker voice name
            model: TTS model to use (bulbul:v1, bulbul:v2)
            pitch: Voice pitch (-0.75 to 0.75)
            pace: Speech speed (0.5 to 2.0)
            loudness: Audio loudness (0.3 to 3.0)
            sample_rate: Sample rate in Hz (8000, 16000, 22050, 24000)
            enable_preprocessing: Enable text preprocessing for mixed-language

        Returns:
            Audio bytes (WAV format)
        """
        try:
            response = self.client.text_to_speech.convert(
                text=text,
                target_language_code=language_code,
                speaker=speaker,
                model=model,
                pitch=pitch,
                pace=pace,
                loudness=loudness,
                speech_sample_rate=sample_rate,
                enable_preprocessing=enable_preprocessing,
            )

            audio_base64 = response.get("audio", "")
            if audio_base64:
                audio_bytes = base64.b64decode(audio_base64)
                return audio_bytes
            else:
                raise ValueError("No audio data in response")
        except Exception as e:
            raise ValueError(f"Text-to-speech failed: {str(e)}")

    async def text_to_speech_stream(
        self,
        text: str,
        language_code: str = "hi-IN",
        speaker: str = "Meera",
        model: str = "bulbul:v1",
    ) -> bytes:
        """
        Stream text to speech (simpler version for real-time use).

        Args:
            text: Text to convert
            language_code: Target language code
            speaker: Speaker voice
            model: TTS model

        Returns:
            Audio bytes
        """
        return await self.text_to_speech(
            text=text,
            language_code=language_code,
            speaker=speaker,
            model=model,
        )

    async def identify_language(self, text: str) -> dict:
        """
        Identify language and script of input text.

        Args:
            text: Input text

        Returns:
            Dictionary with language_code and script
        """
        try:
            response = self.client.text.identify_language(input=text)
            return {
                "language_code": response.get("language_code", "unknown"),
                "script": response.get("script", "unknown"),
            }
        except Exception as e:
            raise ValueError(f"Language identification failed: {str(e)}")

    async def translate_text(
        self,
        text: str,
        source_language_code: str = "auto",
        target_language_code: str = "en-IN",
        model: str = "mayura:v1",
    ) -> dict:
        """
        Translate text between languages.

        Args:
            text: Input text to translate
            source_language_code: Source language (auto for detection)
            target_language_code: Target language code
            model: Translation model (mayura:v1, sarvam-translate:v1)

        Returns:
            Dictionary with translated text
        """
        try:
            response = self.client.text.translate(
                input=text,
                source_language_code=source_language_code,
                target_language_code=target_language_code,
                model=model,
            )
            return {
                "translated_text": response.get("translated_text", ""),
                "source_language_code": response.get("source_language_code", source_language_code),
                "target_language_code": target_language_code,
            }
        except Exception as e:
            raise ValueError(f"Translation failed: {str(e)}")


sarvam_service = SarvamService()
