from typing import List

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


class SentimentAnalysisDetection:
    def _cleanup_user_input(self, user_input: str):
        return user_input.replace(".", " ").replace(",", " ")

    def _find_frustration_keywords(self, chunked_cleaned_user_input_words):
        found_keywords = [
            k in chunked_cleaned_user_input_words for k in FRUSTRATION_KEYWORDS
        ]
        return found_keywords

    def _generate_sentiment_label(self, found_keywords: List[bool], user_input: str):
        frustration_keyword_found_count = found_keywords.count(True)
        if any(found_keywords):
            if frustration_keyword_found_count == 1:
                return f"[User Sentiment: frustrated]\nUser: {user_input}"
            if frustration_keyword_found_count > 1:
                return f"[User Sentiment: Highly frustrated]\nUser: {user_input}"
        return user_input

    def detect_frustration(self, user_input: str):
        chunked_cleaned_user_input_words = self._cleanup_user_input(user_input).split(
            " "
        )
        found_keywords = self._find_frustration_keywords(
            chunked_cleaned_user_input_words
        )
        labelled_user_input = self._generate_sentiment_label(found_keywords, user_input)
        return labelled_user_input
