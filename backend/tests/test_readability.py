import pytest
from app.readability import calculate_readability_metrics, count_syllables


def test_count_syllables_basic():
    assert count_syllables("the") == 1
    assert count_syllables("resume") == 2
    assert count_syllables("engineering") >= 3
    assert count_syllables("orchestration") >= 4
    assert count_syllables("") == 0


def test_empty_or_whitespace_text():
    res = calculate_readability_metrics("")
    assert res["flesch_reading_ease"] == 0.0
    assert res["is_optimal"] is False
    assert "empty" in res["feedback"][0].lower()


def test_insufficient_words_text():
    res = calculate_readability_metrics("Hello world")
    assert res["word_count"] == 2
    assert res["is_optimal"] is False
    assert res["readability_tier"] == "Insufficient Words"


def test_optimal_readability_resume():
    text = (
        "Architected and deployed a distributed microservices platform using Python, Docker, and Kubernetes. "
        "Engineered asynchronous processing queues with Redis, reducing background task latency by 45 percent. "
        "Led a team of five senior software engineers to deliver core cloud infrastructure on AWS."
    )
    res = calculate_readability_metrics(text)
    assert res["word_count"] > 20
    assert res["sentence_count"] >= 3
    assert res["flesch_reading_ease"] > 0
    assert res["flesch_kincaid_grade"] > 0
    assert res["gunning_fog_index"] > 0
    assert isinstance(res["feedback"], list)


def test_dense_complex_text():
    text = (
        "Inextricably conceptualized counter-intuitive multidimensional architectural paradigms utilizing "
        "hyper-parameterized asynchronous computational subroutines encompassing cryptographically decentralized infrastructure."
    )
    res = calculate_readability_metrics(text)
    assert res["complex_word_count"] > 3
    assert res["complex_word_percentage"] > 20.0
