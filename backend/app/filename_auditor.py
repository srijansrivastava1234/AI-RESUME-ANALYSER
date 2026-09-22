"""
ATS File Naming Hygiene & Canonical Standard Auditor.
Evaluates uploaded resume file names against corporate ATS ingestion criteria,
flagging special character hazards, spaces, generic naming, and multi-dot collisions.
"""

import os
import re
from typing import Dict, Any, List

GENERIC_NAMES = {
    "resume", "cv", "my_resume", "my-resume", "resume_final", "resume_v1", "resume_v2",
    "updated_resume", "new_resume", "document", "doc1", "final_resume", "curriculum_vitae"
}

FORBIDDEN_CHARS_REGEX = r'[#%&{}\\\<\>\*\?\/\$\!\'":@\+`\|=\(\)\[\]]'


def audit_filename(filename: str, candidate_name: str = "") -> Dict[str, Any]:
    """
    Audits resume filename against enterprise ATS naming standards.
    Recommended standard: FirstName_LastName_Resume.pdf (ASCII, no spaces/special chars).
    """
    if not filename or not filename.strip():
        return {
            "filename": "",
            "is_valid": False,
            "status": "FAIL",
            "hazards": ["Filename is empty."],
            "suggested_filename": "Candidate_Resume.pdf",
            "score": 0.0
        }

    base_name = os.path.basename(filename).strip()
    name_without_ext, ext = os.path.splitext(base_name)
    ext_lower = ext.lower()

    hazards: List[str] = []
    score = 100.0

    # 1. Valid ATS Extension Check
    if ext_lower not in [".pdf", ".docx", ".doc", ".txt"]:
        hazards.append(f"Non-standard file extension '{ext}'. ATS parsers prefer .pdf or .docx.")
        score -= 40.0

    # 2. Generic Name Check
    normalized_stem = re.sub(r'[^a-z0-9]', '', name_without_ext.lower())
    if normalized_stem in GENERIC_NAMES or name_without_ext.lower() in GENERIC_NAMES:
        hazards.append(f"Generic filename '{base_name}'. ATS databases may overwrite generic resumes; include your full name.")
        score -= 30.0

    # 3. Spaces in Filename
    if " " in name_without_ext:
        hazards.append("Filename contains spaces. Legacy ATS cloud buckets convert spaces to '%20' or truncate paths. Use underscores or hyphens.")
        score -= 15.0

    # 4. Special / Shell Characters
    special_matches = re.findall(FORBIDDEN_CHARS_REGEX, name_without_ext)
    if special_matches:
        hazards.append(f"Filename contains hazardous characters ({', '.join(set(special_matches))}) that fail S3/GCS URL encoding or ATS upload filters.")
        score -= 25.0

    # 5. Multiple Dots
    if name_without_ext.count(".") > 0:
        hazards.append("Multiple dot delimiters detected before extension (e.g. 'resume.v2.pdf'). This can trigger security filters in strict ATS firewalls.")
        score -= 15.0

    # Generate canonical suggestion
    clean_candidate = re.sub(r'[^a-zA-Z0-9]', '_', candidate_name.strip()) if candidate_name else ""
    if clean_candidate:
        clean_candidate = re.sub(r'_+', '_', clean_candidate).strip('_')
        suggested = f"{clean_candidate}_Resume{ext_lower if ext_lower else '.pdf'}"
    else:
        # Clean current name
        clean_stem = re.sub(r'[^a-zA-Z0-9_-]', '_', name_without_ext)
        clean_stem = re.sub(r'_+', '_', clean_stem).strip('_')
        if not clean_stem or clean_stem.lower() in GENERIC_NAMES:
            clean_stem = "FirstName_LastName_Resume"
        suggested = f"{clean_stem}{ext_lower if ext_lower else '.pdf'}"

    score = max(0.0, round(score, 1))
    
    if score >= 90.0:
        status = "EXCELLENT"
    elif score >= 70.0:
        status = "PASS"
    elif score >= 50.0:
        status = "WARNING"
    else:
        status = "CRITICAL"

    return {
        "filename": base_name,
        "extension": ext_lower,
        "is_valid": len(hazards) == 0,
        "status": status,
        "score": score,
        "hazards": hazards,
        "suggested_filename": suggested
    }
