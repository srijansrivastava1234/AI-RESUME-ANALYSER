"""
Multi-Lingual Stopword Filter & Semantic Token Density Engine Module
Audits resumes for information signal-to-noise ratio, lexical diversity (Type-Token Ratio),
and multi-lingual noise across English, Spanish, Portuguese, French, and German.
Filters domain noise to ensure technical resumes maximize information density without
falling into conversational verbosity or unpunctuated keyword stuffing.
"""

import re
import logging
from typing import Dict, Any, List, Set

logger = logging.getLogger("TokenDensityEngine")

# Multi-lingual stopword sets
STOPWORDS: Dict[str, Set[str]] = {
    "en": {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
        "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
        "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
        "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
        "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
        "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
        "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
        "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
        "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
        "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
        "they're", "they've", "this", "those", "through", "to", "too", "under",
        "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
        "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
        "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
        "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
        "your", "yours", "yourself", "yourselves"
    },
    "es": {
        "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por",
        "un", "para", "con", "no", "una", "su", "al", "lo", "como", "mas", "pero",
        "sus", "le", "ya", "o", "este", "si", "porque", "esta", "entre", "cuando",
        "muy", "sin", "sobre", "tambien", "me", "hasta", "hay", "donde", "quien",
        "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra",
        "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mi", "antes", "algunos"
    },
    "pt": {
        "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "nao",
        "uma", "os", "no", "se", "na", "por", "mais", "as", "dos", "como", "mas",
        "ao", "ele", "das", "seu", "sua", "ou", "quando", "muito", "nos", "ja",
        "eu", "tambem", "so", "pelo", "pela", "ate", "isso", "ela", "entre", "depois",
        "sem", "mesmo", "aos", "seus", "quem", "nas", "me", "esse", "eles", "estao"
    },
    "fr": {
        "de", "la", "le", "et", "les", "des", "en", "un", "du", "une", "que", "est",
        "pour", "qui", "dans", "a", "par", "plus", "au", "avec", "ce", "sur", "ne",
        "se", "pas", "sont", "ont", "comme", "mais", "aux", "ou", "on", "sa", "son",
        "ses", "fait", "ete", "aussi", "leur", "nous", "vous", "ils", "sans"
    },
    "de": {
        "der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich", "des",
        "auf", "für", "ist", "im", "dem", "nicht", "ein", "eine", "als", "auch",
        "es", "an", "werden", "aus", "er", "hat", "dass", "sie", "nach", "wird",
        "bei", "einer", "um", "am", "sind", "noch", "wie", "einem", "über", "einen"
    }
}


def detect_language(tokens: List[str]) -> str:
    """
    Infers the primary language by comparing stopword matches across supported languages.
    """
    if not tokens:
        return "en"
    
    token_set = set(tokens)
    scores = {}
    for lang, stopwords in STOPWORDS.items():
        match_count = len(token_set.intersection(stopwords))
        scores[lang] = match_count

    best_lang = max(scores, key=scores.get)
    # Default to English if no clear match
    return best_lang if scores[best_lang] > 0 else "en"


def audit_token_density(text: str, force_lang: str = None) -> Dict[str, Any]:
    """
    Calculates semantic token density, Type-Token Ratio (TTR), and signal-to-noise ratio.

    :param text: Input document text
    :param force_lang: Optional language override ("en", "es", "pt", "fr", "de")
    :return: Dictionary containing density metrics, score, verdict, and recommendations
    """
    if not text or not text.strip():
        return {
            "token_density_score": 0,
            "total_tokens": 0,
            "content_tokens": 0,
            "stopword_count": 0,
            "signal_to_noise_ratio": 0.0,
            "type_token_ratio": 0.0,
            "detected_language": "en",
            "verdict": "Empty Document",
            "recommendations": ["No text found to analyze token density."]
        }

    raw_tokens = re.findall(r'\b[a-zA-Z0-9_\-\+\#\.]+\b', text.lower())
    # Filter pure punctuation/digits for lexical word analysis
    words = [t for t in raw_tokens if re.search(r'[a-zA-Z]', t)]
    total_tokens = len(words)

    if total_tokens < 10:
        return {
            "token_density_score": 30,
            "total_tokens": total_tokens,
            "content_tokens": total_tokens,
            "stopword_count": 0,
            "signal_to_noise_ratio": 1.0,
            "type_token_ratio": 1.0 if total_tokens > 0 else 0.0,
            "detected_language": force_lang or "en",
            "verdict": "Sparse Text",
            "recommendations": ["Document has fewer than 10 words. Add detailed professional accomplishments."]
        }

    detected_lang = force_lang if (force_lang and force_lang in STOPWORDS) else detect_language(words)
    active_stopwords = STOPWORDS.get(detected_lang, STOPWORDS["en"])

    content_words = [w for w in words if w not in active_stopwords]
    content_token_count = len(content_words)
    stopword_count = total_tokens - content_token_count

    # Signal-to-Noise Ratio: content tokens / total tokens
    signal_to_noise_ratio = round(content_token_count / total_tokens, 3)

    # Type-Token Ratio (TTR): unique content words / content words (or unique words / total words)
    unique_words = set(words)
    type_token_ratio = round(len(unique_words) / total_tokens, 3)

    # Benchmarking & Scoring
    # Optimal Signal-to-Noise: 0.55 to 0.75
    # Optimal TTR: 0.35 to 0.65
    score = 100
    recommendations = []

    if signal_to_noise_ratio < 0.45:
        score -= 25
        verdict = "Verbose / Conversational Overload"
        recommendations.append(
            f"High stopword ratio ({round((1 - signal_to_noise_ratio) * 100)}% filler words). Convert conversational narrative into concise, bulleted accomplishment statements."
        )
    elif type_token_ratio < 0.25:
        score -= 30
        verdict = "Keyword Stuffing / Severe Repetition"
        recommendations.append(
            f"Low lexical diversity (TTR: {type_token_ratio}). High repetition of identical words detected. Ground skills into diverse impact contexts."
        )
    elif signal_to_noise_ratio > 0.85 and total_tokens > 50:
        score -= 15
        verdict = "Dense Keyword Dump"
        recommendations.append(
            "Extremely high content-to-stopword ratio (>85%). Ensure resume uses structured grammatical bullets rather than unpunctuated lists of keywords."
        )
    else:
        verdict = "Optimal Technical Density"

    token_density_score = max(0, min(100, score))

    return {
        "token_density_score": token_density_score,
        "total_tokens": total_tokens,
        "content_tokens": content_token_count,
        "stopword_count": stopword_count,
        "signal_to_noise_ratio": signal_to_noise_ratio,
        "type_token_ratio": type_token_ratio,
        "detected_language": detected_lang,
        "verdict": verdict,
        "recommendations": recommendations
    }
