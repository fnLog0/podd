from sarvamai import SarvamAI
from src.config import settings


class SarvamService:
    def __init__(self):
        self.client = SarvamAI(api_subscription_key=settings.SARVAM_API_KEY)

    async def speech_to_text(self, audio_file, language_code: str = "hi-IN") -> dict:
        response = self.client.speech_to_text.translate(
            file=audio_file,
            model="saaras:v2.5",
        )
        return response

    async def text_to_speech(self, text: str, language_code: str = "hi-IN", speaker: str = "shubh") -> bytes:
        response = self.client.text_to_speech.convert(
            text=text,
            target_language_code=language_code,
            model="bulbul:v3",
            speaker=speaker,
        )
        return response


sarvam_service = SarvamService()
