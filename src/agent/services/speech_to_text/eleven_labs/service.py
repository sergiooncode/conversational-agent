import io

import httpx
import structlog
from django.conf import settings
from elevenlabs import ElevenLabs
from pydub import AudioSegment

client = ElevenLabs(
    api_key=settings.ELEVEN_LABS_API_KEY,
)

VOICE_ID = "pNInz6obpgDQGcFmaJgB"

ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"

MODEL_ID = "scribe_v1"  # required

logger = structlog.get_logger(__name__)


def apply_high_pass_filter(audio, cutoff_freq=1000):
    # Apply a high-pass filter to remove low-frequency noise
    return audio.high_pass_filter(cutoff_freq)


# Function to convert Twilio u-law audio to WAV (16kHz, 16-bit PCM)
def twilio_ulaw_to_wav(raw_audio_bytes):
    # Wrap u-law raw bytes into an AudioSegment
    audio = AudioSegment.from_raw(
        io.BytesIO(raw_audio_bytes),
        sample_width=1,  # 8-bit μ-law
        frame_rate=8000,  # 8 kHz sample rate (Twilio)
        channels=1,
        format="ulaw"
    )

    # Convert to 16-bit PCM WAV at 16kHz (common speech format)
    audio = audio.set_frame_rate(16000).set_sample_width(2)  # 16-bit PCM

    # Apply a high-pass filter to remove low-frequency noise (optional)
    audio = apply_high_pass_filter(audio, cutoff_freq=1000)

    # Step 4: Apply Noise Reduction
    # audio = reduce_noise(audio)

    audio.export("../resources/debug_audio.flac", format="flac")

    flac_io = io.BytesIO()
    # audio.export(wav_io, format="wav")
    audio.export(flac_io, format="flac")
    flac_io.seek(0)
    return flac_io


# Function to resample the WAV file to 16kHz if not already
def resample_to_16k(wav_io):
    audio = AudioSegment.from_file(wav_io, format="wav")
    # Ensure it's 16kHz, even if it was originally at a different sample rate
    audio = audio.set_frame_rate(16000)

    audio.export("../resources/debug_resampled_audio.wav", format="wav")

    resampled_io = io.BytesIO()
    audio.export(resampled_io, format="wav")
    resampled_io.seek(0)
    return resampled_io


async def transcribe_audio(audio_bytes: bytes):
    # Use BytesIO to send without saving to disk

    wav_io = twilio_ulaw_to_wav(audio_bytes)
    wav_16k = resample_to_16k(wav_io)

    # Save the final WAV for inspection before sending to ElevenLabs
    with open("../resources/final_audio_for_transcription.wav", "wb") as f:
        f.write(wav_16k.read())

    response = client.speech_to_text.convert(
        model_id=MODEL_ID,
        file=wav_16k
    )
    return response


async def synthesize_speech(text: str):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {"xi-api-key": settings.ELEVEN_LABS_API_KEY, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.aiter_bytes()
