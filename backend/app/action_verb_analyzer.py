"""
Action Verb Dynamism & Repetitive Fatigue Analyzer
Audits bullet points for action verb diversity, detects repetitive verb fatigue,
classifies verb impact tiers (Executive, Engineering, Operational, Weak/Passive),
and recommends dynamic power-verb replacements.
"""

import re
from typing import Dict, Any, List, Set
from collections import Counter

# High-impact verb categorization taxonomy
EXECUTIVE_VERBS: Set[str] = {
    "architected", "spearheaded", "orchestrated", "transformed", "pioneered",
    "scaled", "negotiated", "championed", "formulated", "established",
    "mobilized", "directed", "steered", "empowered", "revitalized"
}

ENGINEERING_VERBS: Set[str] = {
    "engineered", "developed", "deployed", "implemented", "optimized",
    "refactored", "automated", "benchmarked", "designed", "provisioned",
    "containerized", "integrated", "modeled", "profiled", "synchronized"
}

OPERATIONAL_VERBS: Set[str] = {
    "managed", "maintained", "supported", "monitored", "coordinated",
    "executed", "facilitated", "documented", "configured", "reviewed"
}

WEAK_PASSIVE_VERBS: Set[str] = {
    "helped", "assisted", "worked on", "handled", "participated in",
    "involved in", "responsible for", "served as", "contributed to", "tried"
}

POWER_SYNONYM_MAP: Dict[str, List[str]] = {
    "helped": ["Facilitated", "Accelerated", "Co-engineered", "Bolstered"],
    "assisted": ["Collaborated on", "Supported", "Facilitated", "Expedited"],
    "worked on": ["Engineered", "Implemented", "Delivered", "Authored"],
    "managed": ["Orchestrated", "Directed", "Spearheaded", "Governed"],
    "responsible for": ["Owned", "Spearheaded", "Executed", "Accountable for"],
    "handled": ["Resolved", "Administered", "Executed", "Processed"],
}


def extract_bullet_leading_verbs(text: str) -> List[Dict[str, str]]:
    """
    Extracts leading verbs and bullet strings from resume text.
    """
    lines = text.split("\n")
    bullets = []
    
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        
        # Check if line is a bullet or begins with action
        bullet_match = re.match(r"^(?:[\-\*•\u2022\u25E6]\s*|\d+\.\s*)?([A-Za-z]+(?:\s+[A-Za-z]+)?)\b(.*)", cleaned)
        if bullet_match and len(cleaned.split()) >= 4:
            first_words = bullet_match.group(1).lower()
            leading_word = first_words.split()[0]
            
            # Check two-word phrases like 'worked on' or 'responsible for'
            two_word = " ".join(first_words.split()[:2]) if len(first_words.split()) >= 2 else ""
            
            verb = leading_word
            if two_word in WEAK_PASSIVE_VERBS or two_word in POWER_SYNONYM_MAP:
                verb = two_word

            bullets.append({
                "leading_verb": verb,
                "bullet_text": cleaned
            })
            
    return bullets


def audit_action_verbs(text: str) -> Dict[str, Any]:
    """
    Audits resume bullet action verbs for variety, tier distribution, and repetitive fatigue.
    """
    extracted = extract_bullet_leading_verbs(text)
    total_bullets = len(extracted)
    
    if total_bullets == 0:
        return {
            "action_verb_score": 50,
            "variety_ratio": 0.0,
            "total_bullets_analyzed": 0,
            "verb_frequency": {},
            "fatigued_verbs": [],
            "weak_verbs_detected": [],
            "tier_breakdown": {
                "executive": 0,
                "engineering": 0,
                "operational": 0,
                "weak": 0,
                "unclassified": 0
            },
            "recommendations": ["No bullet points found. Use bullet points starting with strong action verbs."]
        }
        
    verbs = [b["leading_verb"] for b in extracted]
    counts = Counter(verbs)
    unique_verbs = len(counts)
    variety_ratio = round(unique_verbs / total_bullets, 2)
    
    # Identify repetitive fatigue (same leading verb used > 2 times)
    fatigued_verbs = [
        {"verb": verb, "count": cnt, "warning": f"'{verb.capitalize()}' is repeated {cnt} times across bullets."}
        for verb, cnt in counts.items() if cnt > 2
    ]
    
    # Classify verbs into tiers
    tier_counts = {"executive": 0, "engineering": 0, "operational": 0, "weak": 0, "unclassified": 0}
    weak_detected = []
    
    for verb in verbs:
        if verb in EXECUTIVE_VERBS:
            tier_counts["executive"] += 1
        elif verb in ENGINEERING_VERBS:
            tier_counts["engineering"] += 1
        elif verb in OPERATIONAL_VERBS:
            tier_counts["operational"] += 1
        elif verb in WEAK_PASSIVE_VERBS or verb in POWER_SYNONYM_MAP:
            tier_counts["weak"] += 1
            if verb not in [w["verb"] for w in weak_detected]:
                weak_detected.append({
                    "verb": verb,
                    "suggested_replacements": POWER_SYNONYM_MAP.get(verb, ["Engineered", "Spearheaded", "Delivered"])
                })
        else:
            tier_counts["unclassified"] += 1
            
    # Calculate score
    penalties = 0
    recommendations: List[str] = []
    
    if fatigued_verbs:
        fatigue_penalty = sum(max(0, f["count"] - 1) * 8 for f in fatigued_verbs)
        penalties += min(35, fatigue_penalty)
        recommendations.append(f"Diversify repetitive opening verbs: {', '.join([f['verb'] for f in fatigued_verbs])}.")
        
    if weak_detected:
        penalties += min(35, len(weak_detected) * 10)
        recommendations.append(f"Replace passive phrases ({', '.join([w['verb'] for w in weak_detected])}) with active power verbs.")
        
    if variety_ratio < 0.6 and total_bullets >= 4:
        penalties += 15
        recommendations.append("Action verb variety ratio is low. Aim for distinct verbs at the start of each bullet point.")
        
    score = max(0, 100 - penalties)
    
    return {
        "action_verb_score": score,
        "variety_ratio": variety_ratio,
        "total_bullets_analyzed": total_bullets,
        "verb_frequency": dict(counts.most_common(10)),
        "fatigued_verbs": fatigued_verbs,
        "weak_verbs_detected": weak_detected,
        "tier_breakdown": tier_counts,
        "recommendations": recommendations
    }
