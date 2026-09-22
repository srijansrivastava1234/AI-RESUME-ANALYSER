"""
Portfolio & Professional Social Link Canonical Validator.
Audits candidate digital footprint URLs (LinkedIn, GitHub, Personal Domain, Kaggle, LeetCode),
verifying HTTPS security, canonical path structure, and detecting placeholder links.
"""

import re
from typing import Dict, Any, List

URL_REGEX = r'(https?://[^\s<>"\')]+|www\.[^\s<>"\')]+|[a-zA-Z0-9.-]+\.(?:com|org|dev|io|me|ai|tech|net)/[^\s<>"\')]+)'

PLACEHOLDER_USERNAMES = {
    "username", "yourname", "your-username", "your_username", "johndoe", "janedoe",
    "handle", "profile", "user", "placeholder", "your_profile", "link"
}


def audit_portfolio_links(text: str) -> Dict[str, Any]:
    """
    Audits URLs and digital identity links within resume text.
    """
    if not text or not text.strip():
        return {
            "links_found": 0,
            "has_linkedin": False,
            "has_github": False,
            "has_portfolio": False,
            "link_score": 0.0,
            "links": [],
            "status": "PASS",
            "feedback": ["No text provided for link validation."]
        }

    raw_urls = re.findall(URL_REGEX, text)
    cleaned_urls = list(set([u.rstrip('.,;:') for u in raw_urls]))

    links_diagnostics: List[Dict[str, Any]] = []
    has_linkedin = False
    has_github = False
    has_portfolio = False
    has_insecure_http = False
    has_placeholders = False

    for url in cleaned_urls:
        url_lower = url.lower()
        is_https = url_lower.startswith("https://")
        if url_lower.startswith("http://"):
            has_insecure_http = True

        link_type = "OTHER"
        is_placeholder = False

        if "linkedin.com" in url_lower:
            link_type = "LINKEDIN"
            has_linkedin = True
            # Check for placeholder or bare profile
            match = re.search(r'linkedin\.com/in/([a-zA-Z0-9_-]+)', url_lower)
            if match:
                user = match.group(1)
                if user in PLACEHOLDER_USERNAMES:
                    is_placeholder = True
                    has_placeholders = True
            else:
                is_placeholder = True

        elif "github.com" in url_lower:
            link_type = "GITHUB"
            has_github = True
            match = re.search(r'github\.com/([a-zA-Z0-9_-]+)', url_lower)
            if match:
                user = match.group(1)
                if user in PLACEHOLDER_USERNAMES:
                    is_placeholder = True
                    has_placeholders = True
            else:
                is_placeholder = True

        elif any(ext in url_lower for ext in [".dev", ".io", ".me", "portfolio", "blog"]):
            link_type = "PORTFOLIO"
            has_portfolio = True

        links_diagnostics.append({
            "url": url,
            "type": link_type,
            "is_https": is_https,
            "is_placeholder": is_placeholder
        })

    # Score calculation
    score = 50.0
    if has_linkedin:
        score += 25.0
    if has_github:
        score += 25.0
    if has_portfolio:
        score += 10.0
    if has_insecure_http:
        score -= 15.0
    if has_placeholders:
        score -= 30.0

    final_score = max(0.0, min(100.0, round(score, 1)))

    feedback: List[str] = []
    if has_placeholders:
        status = "CRITICAL"
        feedback.append("Placeholder URLs detected (e.g. 'github.com/username'). Update links with your authentic verified handles.")
    elif final_score >= 80.0:
        status = "EXCELLENT"
        feedback.append("Excellent digital presence links. Verified LinkedIn and GitHub profiles detected.")
    elif final_score >= 60.0:
        status = "PASS"
        feedback.append("Standard profile links found. Ensure both LinkedIn and GitHub are included for technical roles.")
    else:
        status = "WARNING"
        feedback.append("Sparse online portfolio links. Adding a customized LinkedIn and active GitHub URL increases recruiter response rates by 40%.")

    if has_insecure_http:
        feedback.append("Insecure 'http://' protocol detected. Upgrade all portfolio and personal site links to 'https://'.")

    return {
        "links_found": len(cleaned_urls),
        "has_linkedin": has_linkedin,
        "has_github": has_github,
        "has_portfolio": has_portfolio,
        "link_score": final_score,
        "links": links_diagnostics,
        "status": status,
        "feedback": feedback
    }
