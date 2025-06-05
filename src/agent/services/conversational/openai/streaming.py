import os

from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAPI_API_KEY"))


async def stream_llm_response(user_input):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_input}],
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
