from agent.services.sentiment_analysis.detect import detect_frustration


def test_detect_frustration_returns_frustration():
    user_input = (
        "The issue was that I rented a car a few weeks ago, put down a "
        "deposit but i haven't got a refund of the deposit yet which is unacceptable."
    )
    enriched_user_input = detect_frustration(user_input)

    assert (
        enriched_user_input
        == "[User Sentiment: frustrated]\nUser: The issue was that I "
        "rented a car a few weeks ago, put down a deposit but i "
        "haven't got a refund of the deposit yet which is unacceptable."
    )
