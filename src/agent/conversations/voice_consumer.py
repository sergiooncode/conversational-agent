import base64
import json
import os
import uuid

import structlog
from channels.generic.websocket import AsyncWebsocketConsumer

from agent.services.conversational.openai.streaming import stream_llm_response
from agent.services.speech_to_text.eleven_labs.service import (
    transcribe_audio,
    synthesize_speech,
)

logger = structlog.get_logger(__name__)


class AudioConsumer(AsyncWebsocketConsumer):
    audio_buffer = None
    transcript_text = None

    async def connect(self):
        await self.accept()
        logger.info("WebSocket connected from Twilio")
        self.audio_buffer = b""
        self.transcript_text = ""

    async def disconnect(self, close_code):
        logger.info("WebSocket disconnected")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
                if data["event"] == "media":
                    payload = data["media"]["payload"]
                    audio_bytes = base64.b64decode(payload)
                    self.audio_buffer += audio_bytes
                    logger.info(
                        f"Received {len(audio_bytes)} bytes of audio and "
                        f"accumulated {len(self.audio_buffer)}"
                    )
                    # Now pass `audio_bytes` to your speech-to-text engine or buffer
                    if (
                        len(self.audio_buffer) > 40000
                    ):  # arbitrary threshold for full utterance
                        logger.info(audio_bytes)
                        transcript = await transcribe_audio(self.audio_buffer)
                        self.transcript_text += transcript.text
                        logger.info(
                            "audio_consumer_stt_transcript",
                            message=self.transcript_text,
                        )

                        if len(self.transcript_text) != 0:
                            # response_text = ""
                            # async for chunk in stream_llm_response(transcript.text):
                            #    response_text += chunk
                            #
                            # tts_audio = await synthesize_speech(response_text)
                            #
                            # filename = f"../resources/tts_{uuid.uuid4()}.mp3"
                            # with open(filename, "wb") as f:
                            #    async for chunk in tts_audio:
                            #        f.write(chunk)
                            # logger.info(f"Audio response ready at: {filename}")
                            # await self.close()
                            pass
                        else:
                            logger.warning(
                                "audio_consumer_receive", message="Empty transcript"
                            )
                else:
                    logger.debug(f"Received event: {data['event']}")
            except Exception as e:
                import traceback

                traceback.print_exc()
                logger.error(f"Failed to handle WebSocket message: {e}")
