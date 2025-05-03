# conversational-agent

## Setup instructions
- Run command:
```
make recreate
```

- Run tests:
```
make test
```

## Create a conversation with a bot given a function

- Create a conversation.

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

- As a human user as a question about an issue to the Customer Support of the fictional business:

```
curl -X PATCH http://localhost:8001/api/conversations/9701444a-9618-428c-9a24-eca0636fbc9d/ \
  -H "Content-Type: application/json" \
  -d '{"message": "i have an issue"}'
```

It should return a response like:
```
{
"bot_message": "I'm here to help! Could you please provide me with a bit more information? Let me know your order number, the category of the problem, a brief description of the issue, and how urgent it is. That way, I can assist you better!"
}
```

## System architecture overview



## Explanation of key design decisions

- Postgres and storing conversation and extracted data in JSON
- Using OpenAI Agents SDK for conversation flow.
- Django Signals to decouple storing raw conversation and summary in DB

## Description of potential improvements
- Store conversations as the product scales. Postgres JSONB field allows max size 1 GB.
https://www.dbvis.com/thetable/everything-you-need-to-know-about-the-postgres-jsonb-data-type/#:~:text=What%20is%20the%20size%20limit,text%20%2C%20which%20is%201%20GB.

- It makes sense to have a model HumanUser but probably it shouldn't be part of this agent service.


## Sample conversations demonstrating the bot's capabilities

