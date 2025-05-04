import uuid

from django.conf import settings
from elevenlabs import ElevenLabs

client = ElevenLabs(
    api_key=settings.ELEVEN_LABS_API_KEY,
)


class TextToSpeechService:
    def __init__(
        self,
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        output_format="mp3_44100_128",
        model_id="eleven_multilingual_v2",
    ):
        self._voice_id = voice_id
        self._output_format = output_format
        self._model_id = model_id

    def _convert(self, text: str):
        response = client.text_to_speech.convert(
            text=text,
            voice_id=self._voice_id,
            output_format=self._output_format,
            model_id=self._model_id,
        )
        return response

    def _save_stream_to_file(self, response, speech_id: str):
        save_file_path = f"../resources/{speech_id}.mp3"
        # Writing the audio to a file
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        print(f"{save_file_path}: A new audio file was saved successfully!")
        # Return the path of the saved audio file
        return save_file_path

    def convert_and_save_to_file(self, text: str):
        speech_recording_id = uuid.uuid4()
        response = self._convert(text)
        return self._save_stream_to_file(response, speech_recording_id)
