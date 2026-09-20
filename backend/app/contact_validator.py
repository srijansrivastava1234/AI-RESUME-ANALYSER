"""
Candidate Contact & Profile Link Security Auditor
Validates candidate contact coordinates against RFC 5322 email specifications,
ITU-T E.164 international telephone numbering, and HTTPS profile link security.
Protects against ATS ingestion failure, spam blacklisting, and recruiter knockout.
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

# RFC 5322 Simplified Regex for standard email syntax
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Placeholder patterns indicative of template resumes
PLACEHOLDER_EMAILS = {
    "yourname@email.com", "example@example.com", "your.name@gmail.com",
    "john.doe@example.com", "email@address.com", "candidate@email.com",
    "user@domain.com", "your_email@gmail.com"
}

DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "throwawaymail.com",
    "guerrillamail.com", "yopmail.com", "trashmail.com", "sharklasers.com"
}

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "adf.ly"
}

PLACEHOLDER_USERNAMES = {
    "yourname", "your-name", "username", "in-yourname", "your_profile",
    "john-doe", "placeholder", "your-username", "johndoe"
}


def audit_email(email: Optional[str]) -> Dict[str, Any]:
    """
    Audit candidate email for RFC 5322 compliance, disposable domains, and placeholder values.
    """
    if not email or not email.strip():
        return {
            "email": None,
            "is_valid": False,
            "is_placeholder": False,
            "is_disposable": False,
            "penalty": 35,
            "issue": "Missing email address in resume header."
        }

    email_clean = email.strip()
    email_lower = email_clean.lower()

    if email_lower in PLACEHOLDER_EMAILS or any(p in email_lower for p in ["yourname", "your.name", "john.doe"]):
        return {
            "email": email_clean,
            "is_valid": False,
            "is_placeholder": True,
            "is_disposable": False,
            "penalty": 25,
            "issue": f"Placeholder email address detected: '{email_clean}'. Replace with your verified email."
        }

    if not EMAIL_REGEX.match(email_clean):
        return {
            "email": email_clean,
            "is_valid": False,
            "is_placeholder": False,
            "is_disposable": False,
            "penalty": 30,
            "issue": f"Malformed email address: '{email_clean}' fails RFC 5322 syntax validation."
        }

    domain = email_lower.split("@")[-1]
    if domain in DISPOSABLE_DOMAINS:
        return {
            "email": email_clean,
            "is_valid": False,
            "is_placeholder": False,
            "is_disposable": True,
            "penalty": 40,
            "issue": f"Disposable email domain detected: '{domain}'. Enterprise ATS platforms automatically blacklist temporary inboxes."
        }

    return {
        "email": email_clean,
        "is_valid": True,
        "is_placeholder": False,
        "is_disposable": False,
        "penalty": 0,
        "issue": None
    }


def audit_phone(phone: Optional[str]) -> Dict[str, Any]:
    """
    Audit telephone number for ITU-T E.164 international standard format and country code presence.
    """
    if not phone or not phone.strip():
        return {
            "phone": None,
            "e164_formatted": None,
            "has_country_code": False,
            "is_valid": False,
            "is_placeholder": False,
            "penalty": 25,
            "issue": "Missing telephone number in resume header."
        }

    raw = phone.strip()
    # Strip formatting characters: spaces, dashes, parentheses, dots
    digits_only = re.sub(r"[^\d+]", "", raw)

    # Check for placeholder sequences
    if re.search(r"123[ -.]?456[ -.]?7890|000[ -.]?000|999[ -.]?999|555[ -.]?0199", raw):
        return {
            "phone": raw,
            "e164_formatted": None,
            "has_country_code": False,
            "is_valid": False,
            "is_placeholder": True,
            "penalty": 25,
            "issue": f"Placeholder telephone number detected: '{raw}'."
        }

    has_country_code = digits_only.startswith("+")
    num_digits = len(re.sub(r"\D", "", digits_only))

    if num_digits < 7 or num_digits > 15:
        return {
            "phone": raw,
            "e164_formatted": None,
            "has_country_code": has_country_code,
            "is_valid": False,
            "is_placeholder": False,
            "penalty": 20,
            "issue": f"Invalid telephone digit count ({num_digits}). Must conform to ITU-T standard (7-15 digits)."
        }

    # Format into canonical E.164 if country code is present
    if has_country_code:
        e164_canonical = "+" + re.sub(r"\D", "", digits_only)
        penalty = 0
        issue = None
    else:
        # Default assume domestic without country prefix
        e164_canonical = None
        penalty = 10
        issue = f"Missing international country calling code in '{raw}'. Prefix with '+' and country code (e.g. +1, +44, +91) for global ATS."

    return {
        "phone": raw,
        "e164_formatted": e164_canonical,
        "has_country_code": has_country_code,
        "is_valid": True,
        "is_placeholder": False,
        "penalty": penalty,
        "issue": issue
    }


def audit_profile_links(links: List[str]) -> List[Dict[str, Any]]:
    """
    Audit external links (LinkedIn, GitHub, Portfolio) for HTTPS encryption,
    placeholder slugs, and suspicious URL shorteners.
    """
    audited_links = []
    for link in links:
        if not link or not link.strip():
            continue
        url = link.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        parsed = urlparse(url)
        domain = (parsed.netloc or "").lower()
        path = parsed.path.lower()

        is_https = parsed.scheme == "https"
        is_shortener = any(shortener in domain for shortener in URL_SHORTENERS)
        
        # Check placeholder in path
        path_slugs = [s for s in path.split("/") if s]
        is_placeholder = any(slug in PLACEHOLDER_USERNAMES for slug in path_slugs)

        penalty = 0
        issues = []

        if not is_https:
            penalty += 15
            issues.append(f"Insecure protocol (HTTP) in '{url}'. Use secure HTTPS to prevent ATS parser security warnings.")

        if is_shortener:
            penalty += 25
            issues.append(f"URL shortener domain detected ('{domain}'). Automated screening algorithms flag redirect shorteners as spam/phishing.")

        if is_placeholder:
            penalty += 20
            issues.append(f"Placeholder username slug in '{url}'. Update with your active personal profile URL.")

        # Identify profile type
        if "linkedin.com" in domain:
            link_type = "LinkedIn"
        elif "github.com" in domain:
            link_type = "GitHub"
        elif "gitlab.com" in domain or "bitbucket.org" in domain:
            link_type = "Version Control"
        elif any(b in domain for b in ["portfolio", "dev", "me", "io"]):
            link_type = "Portfolio"
        else:
            link_type = "External Link"

        audited_links.append({
            "url": url,
            "type": link_type,
            "is_https": is_https,
            "is_shortener": is_shortener,
            "is_placeholder": is_placeholder,
            "penalty": penalty,
            "issues": issues
        })

    return audited_links


def audit_candidate_contact(
    email: Optional[str] = None,
    phone: Optional[str] = None,
    links: Optional[List[str]] = None,
    text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Comprehensive ATS candidate contact ingestion and security auditor.
    Extracts email, phone, and links from text if not explicitly provided.
    """
    extracted_email = email
    extracted_phone = phone
    extracted_links = links or []

    # If text is provided, perform automated regex extraction
    if text:
        if not extracted_email:
            email_match = re.search(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b", text)
            if email_match:
                extracted_email = email_match.group(0)

        if not extracted_phone:
            phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
            if phone_match:
                extracted_phone = phone_match.group(0)

        if not extracted_links:
            url_matches = re.findall(r"(?:https?://|www\.)[^\s,]+", text)
            clean_matches = [m.rstrip(".,;)") for m in url_matches]
            extracted_links.extend(clean_matches)

    email_audit = audit_email(extracted_email)
    phone_audit = audit_phone(extracted_phone)
    links_audit = audit_profile_links(extracted_links)

    total_penalty = email_audit["penalty"] + phone_audit["penalty"]
    for l in links_audit:
        total_penalty += l["penalty"]

    # Deduct up to max 100 pts
    reliability_index = max(0, 100 - total_penalty)

    if reliability_index >= 85:
        status = "OPTIMAL"
    elif reliability_index >= 60:
        status = "WARNING"
    else:
        status = "CRITICAL"

    actionable_recommendations = []
    if email_audit["issue"]:
        actionable_recommendations.append(email_audit["issue"])
    if phone_audit["issue"]:
        actionable_recommendations.append(phone_audit["issue"])
    for l in links_audit:
        actionable_recommendations.extend(l["issues"])

    if not links_audit:
        actionable_recommendations.append(
            "No LinkedIn or GitHub profile link detected. Adding verified professional profiles increases recruiter engagement by 40%."
        )

    return {
        "reliability_index": reliability_index,
        "status": status,
        "email_audit": email_audit,
        "phone_audit": phone_audit,
        "links_audit": links_audit,
        "recommendations": actionable_recommendations
    }
