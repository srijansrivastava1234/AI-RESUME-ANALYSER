def calculate_threat_score(transcript: str) -> dict:
    """
    Analyzes the transcript text and returns the threat score along with matched categories.
    Scoring logic:
    - Urgency category matches (e.g., immediate, block, suspend, arrest, hurry) -> +30 points
    - Financial/Action category matches (e.g., OTP, pin, transfer, anydesk, download, bank) -> +40 points
    - Authority category matches (e.g., CBI, police, customs, manager, FedEx) -> +30 points
    """
    urgency_keywords = ["immediate", "block", "suspend", "arrest", "hurry", "urgent", "now"]
    action_keywords = ["otp", "pin", "transfer", "anydesk", "download", "bank", "card", "password", "send"]
    authority_keywords = ["cbi", "police", "customs", "manager", "fedex", "support", "agent", "officer"]

    text_lower = transcript.lower()

    matched_urgency = [word for word in urgency_keywords if word in text_lower]
    matched_action = [word for word in action_keywords if word in text_lower]
    matched_authority = [word for word in authority_keywords if word in text_lower]

    score = 0
    categories_detected = []

    if matched_urgency:
        score += 30
        categories_detected.append("Urgency")
    if matched_action:
        score += 40
        categories_detected.append("Financial/Action Required")
    if matched_authority:
        score += 30
        categories_detected.append("Impersonation/Authority")

    return {
        "score": score,
        "categories": categories_detected,
        "matches": {
            "urgency": matched_urgency,
            "action": matched_action,
            "authority": matched_authority
        }
    }
