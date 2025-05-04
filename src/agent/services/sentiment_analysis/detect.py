FRUSTRATION_KEYWORDS = [
    "unacceptable",
    "angry",
    "frustrated",
    "frustrating",
    "ridiculous",
    "disappointed",
    "i want a refund",
    "annoyed",
    "annoying",
    "i'm tired of",
    "this is the third time",
    "still waiting",
    "why haven't you",
    "no response",
    "not happy",
]


def detect_frustration(user_input: str):
    cleaned_user_input = user_input.replace(".", " ").replace(",", " ")
    chunked_user_input_words = cleaned_user_input.split(" ")
    found_keywords = [k in chunked_user_input_words for k in FRUSTRATION_KEYWORDS]
    frustration_keyword_found = any(found_keywords)
    if frustration_keyword_found:
        return f"[User Sentiment: frustrated]\nUser: {user_input}"
    return user_input
