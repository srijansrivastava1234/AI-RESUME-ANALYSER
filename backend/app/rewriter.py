import os
import json
import logging
from typing import Optional
import google.generativeai as genai

logger = logging.getLogger("BulletOptimizer")

ACTION_VERB_MAP = {
    "helped": "Spearheaded",
    "worked on": "Architected",
    "responsible for": "Engineered",
    "handled": "Orchestrated",
    "managed": "Directed",
    "did": "Executed",
    "made": "Developed",
    "assisted": "Collaborated on",
    "looked after": "Maintained",
    "fixed": "Resolved"
}

def optimize_bullet_heuristic(bullet: str, target_role: Optional[str] = None) -> dict:
    """
    Offline heuristic rule engine for rewriting resume bullet points into XYZ format.
    """
    clean = bullet.strip().rstrip(".")
    lower = clean.lower()
    
    # Replace weak action verbs if detected at the beginning
    optimized_text = clean
    for weak_verb, strong_verb in ACTION_VERB_MAP.items():
        if lower.startswith(weak_verb):
            optimized_text = strong_verb + clean[len(weak_verb):]
            break
            
    # Add quantification placeholder if not present
    if not any(char.isdigit() or char == "%" for char in clean):
        optimized_text += ", improving system efficiency by 25% and reducing operational turnaround time."
        
    return {
        "original": bullet,
        "optimized": optimized_text,
        "action_verb_used": optimized_text.split()[0] if optimized_text else "Engineered",
        "framework": "XYZ Formula (Accomplished [X] measured by [Y], by doing [Z])",
        "feedback": "Transformed passive statement into high-impact, quantifiable bullet point."
    }

def optimize_bullet_point(bullet: str, target_role: Optional[str] = None) -> dict:
    """
    Rewrites a single bullet point using Gemini 1.5 Flash or falls back to heuristic engine.
    """
    if not bullet or len(bullet.strip()) < 5:
        raise ValueError("Bullet point text must be at least 5 characters long.")
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return optimize_bullet_heuristic(bullet, target_role)
        
    prompt = f"""
    You are an executive resume coach. Rewrite the following resume bullet point into a high-impact,
    quantifiable achievement following Google's XYZ formula: "Accomplished [X] as measured by [Y], by doing [Z]".
    
    Target Role: {target_role if target_role else 'Software Engineer / Tech Professional'}
    Original Bullet Point: "{bullet}"
    
    Return strict JSON with this schema:
    {{
      "original": "{bullet}",
      "optimized": "Optimized bullet point text here",
      "action_verb_used": "Leading action verb",
      "framework": "XYZ Formula",
      "feedback": "Why this change improves recruiter impact"
    }}
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        logger.warning(f"Gemini API bullet rewrite error: {e}. Using heuristic fallback.")
        return optimize_bullet_heuristic(bullet, target_role)
