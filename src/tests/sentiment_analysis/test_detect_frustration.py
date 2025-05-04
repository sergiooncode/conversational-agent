from agent.services.sentiment_analysis.detect import SentimentAnalysisDetection


def test_detect_frustration_returns_frustrated_label():
    user_input = (
        "The issue was that I rented a car a few weeks ago, put down a "
        "deposit but i haven't got a refund of the deposit yet which is unacceptable."
    )

    enriched_user_input = SentimentAnalysisDetection().detect_frustration(user_input)

    assert (
        enriched_user_input
        == "[User Sentiment: frustrated]\nUser: The issue was that I "
        "rented a car a few weeks ago, put down a deposit but i "
        "haven't got a refund of the deposit yet which is unacceptable."
    )


def test_detect_high_frustration_returns_highly_frustrated_label():
    user_input = (
        "The issue was that I rented a car a few weeks ago, put down a "
        "high amount as deposit which was annoying but i haven't got a "
        "refund of the deposit yet which is unacceptable."
    )

    enriched_user_input = SentimentAnalysisDetection().detect_frustration(user_input)

    assert (
        enriched_user_input
        == "[User Sentiment: Highly frustrated]\nUser: The issue was that I rented a "
        "car a few weeks ago, put down a high amount as deposit which was "
        "annoying but i haven't got a refund of the deposit yet which is unacceptable."
    )


def test_detect_frustration_returns_no_frustration_detected_label():
    user_input = (
        "The issue was that I rented a car a few weeks ago and i didn't received "
        "an email with the bills and closure details."
    )
    enriched_user_input = SentimentAnalysisDetection().detect_frustration(user_input)

    assert enriched_user_input == user_input
