# conversational-agent

## Setup instructions

Note: an environment variable OPENAPI_API_KEY with a valid API key for the OpenAI API platform is necessary. Also
an environment variable ELEVEN_LABS_API_KEY is necessary to use Text-to-Speech on the
`/api/conversations/<conversation_id>/follow-up-speech/` endpoint.

Note: there is a `How to test` section with cURL commands to test.

- Run command:
```
make recreate
```

- Run tests:
```
make test
```

## System architecture overview

- The Conversational agent service was anchored in the Customer Support use case which can be seen
in prompts and architecture of agents.

- As the diagram below shows, the Conversational agent service is exposed through a REST API.

- There are 2 sets of endpoints corresponding to 2 different flows: Conversational flow and Text-to-speech.

- In the Conversational flow there are endpoints to create a conversation between a human user and a bot, and
a endpoint to send/add a message to a conversation which returns a response from the bot. This flow relies
con the OpenAI Agents platform accessed through the Agents SDK.

- The Conversational flow relies on a 3 agent architecture. Since the Customer Support was used the agents are:
`Customer Support Triaging and Info Collector`, `Customer Support Info Structurer` and
`Customer Support User Reassurance and Send Off`

- In the TTS there is only one endpoint to generate a speech recording with a follow-up to that conversation
and saves the recording file currently in the local file system. This flow relies on the ElevenLabs API
accessed through its Python client.

- This TTS flow is not fully defined since a user could only listen to the recording but nothing else.
The recording is generated given a text based on the summary of the conversation and a static template
but this is very limited. More definition on the exact use case would be necessary and
further development are needed and maybe a proper call with a TTS agent could set up.

- The conversations as the human user sends messages and the agent answers are stored in PostgreSQL.
The summary is extracted by the agent `Customer Support Info Structurer` using the tools feature of OpenAI Agents
SDK which then is saved in a summary JSON field of the conversation model instance.

### Diagram

![Diagram](blueprint/diagram.png)

### Domain modelling:

- The Intelligent Conversational Agent application was split in 4 domains: conversations, bots,
human users and prompts. Since Django was used, 4 applications were created so the 4 domains can
evolve somehow independently although some of them are related to each other mainly through FK
relations in DB.

![Domains](blueprint/domains.png)

## Explanation of key design decisions

- Using OpenAI Agents SDK for conversation flow was a decision. I debated with myself between OpenAI and Anthropic
platforms and I landed on OpenAI because both the Agents SDK official docs and the examples in the official
OpenAI repo caught my eye.

- The SDK seems to be evolving and its documentation with it.
Also it seems that they use have something called `agentkit` as part of the SDK and some examples online
show it but it's not in the official docs.

- Structure output from agents based on LLMs. LLM produce natural language and, unless specific instructions are
given to it and features of the AI platform are used (specific prompt instructions, tools, output type),
doesn't abide by the instructions by default.

- The agents, at least on OpenAI agents framework, are stateless. The handoffs feature is slightly misleading
because it sounds as if the agents coordinate themselves. The consequence of the above is that they have to be
coordinated so the right agent is used to give an answer even if the handoffs feature is used. That's the reason
why a multi-agent controller was added towards the end of the development and it needs more testing.

- Regarding the context and memory of the agents the whole conversation history up to that point
is passed as input to the agent that runs to generate an answer. That conversation history is formatted
in a structured way like `User: <message>` or `Assistant: <message>`. In the prompts for the 3 agents
is indicated that the conversation history is part of the input they receive.

- The agent `Customer Support Triaging and Info Collector` which is the first to run already receives the
whole conversation history.

- Postgres and storing conversation messages in JSON. The field `raw_conversation` is a JSONB field with list
as default. After doing some research the append of an item in that field should be efficient. Also the
JSONB field has a max size that seems high enough (1 GB).

- Async use in PATCH `/api/conversations/<id>/` endpoint because Runner.run is async. I realized later there is
a Runner.run_sync so making the endpoint async maybe was not 100% necessary.

### Bonus points

- Sentiment analysis detection was added in a very simplistic way by just trying to find sentiment keywords
(frustrated, dissapointed, etc) in customer messages and enriching that message with the
sentiment information in structured format (like [User Sentiment: highly frustrated]... + message).

- I started working on RAG to improve the agent system answers. I found a knowledge base with customer
support answers on Kaggle. I researched a "cheap" way to implement RAG using a OS LLM model and loading
the embeddings in memory.

- The RAG service would compare the user's comment with embeddings of
the answers in the mentioned knowledge base using a simple LLM called all-MiniLM-L6-v2. A RAG service could be
defined which would load answers embeddings in memory (in the future a Vector DB API service could be
used), then the `ConversationPartialUpdateManager` would call that RAG service


## Description of potential improvements

- Storing conversations as the product scales. Postgres JSONB field allows max size 1 GB.

- The API has no authentication and that's not right. It's should be first identified who is the
user and who is the client of the API, whoever owns the authentication method artifact (API key, token, etc)
will be the client since through that authentication method we know is "them" using the API.

- I had plans for the Prompt Django model but it's currently not used. The prompts for the 3-agent system are mainly static.
If the prompts were to be generated dynamically maybe the Prompt Django model could come in handy. 

- Increasing the test coverage would be necessary.

## How to test

- Create a conversation with the Customer Support of the fictional business.

Note: The only valid functions is customer_support, but only customer_support

```
curl -X POST http://localhost:8001/api/conversations/ \
  -H "Content-Type: application/json" \
  -d '{"function": "customer_support"}'
```

It should return a response like:
```
{
"conversation_id":"9701444a-9618-428c-9a24-eca0636fbc9d",
"bot_id":"1e575937-32a4-4ffe-b09f-48a95dbedc91",
"human_user_id":"8c37b9b4-4c6f-4702-9f84-57d5cbbf81f8"
}
```

- A human user can make a comment to the Customer Support in the context of a conversation/issue using
a request like below with the conversation_id returned in the previous request:

```
curl -X PATCH http://localhost:8001/api/conversations/9701444a-9618-428c-9a24-eca0636fbc9d/ \
  -H "Content-Type: application/json" \
  -d '{"message": "i have an issue"}'
```

It returns a response like below following certain pre-configured instructions and the conversation
history up to that point in the conversation:
```
{
"bot_message": "I'm here to help! Could you please provide me with a bit more information? Let me know your order number, the category of the problem, a brief description of the issue, and how urgent it is. That way, I can assist you better!"
}
```

- A human user can request a follow up call (a speech recording for now) on a conversation previously
created:

```
curl -X POST http://localhost:8001/api/conversations/9701444a-9618-428c-9a24-eca0636fbc9d/follow-up-speech/
```

It returns a speech recording id containing a follow up speech on the conversation whose id is passed,
the actual recording file is saved in the `resources` folder at the top level from where
it can be played:

```
{
"speech_id": "a84ba83d-b27e-43d5-9706-cfac53ea37bc"
}
```

## Sample conversations demonstrating the bot's capabilities

- Sample conversation between the Customer Support agent and a human user:

Note: the raw_conversation field is a list and the messages order is the lower the index in the list the earlier the message

![Sample 1](blueprint/conversation_capabilities_sample.png)

- Sample text to speech

Click [here](https://github.com/sergiooncode/conversational-agent/blob/main/blueprint/daa314c2-3723-4b63-afff-a5430616416a.mp3)
to download the raw file which then can be played on your computer. To download click on the arrow down button on
the far right seen below:

![Sample 1](blueprint/download_raw_file.png)


