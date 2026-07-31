import os
import json
import logging
import google.generativeai as genai
from typing import Optional

logger = logging.getLogger("ResumeAnalyzer")

# Try to load environment variables (FastAPI will load .env usually, but we safeguard here)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set. The backend will run in simulation mode.")

ANALYSIS_PROMPT_TEMPLATE = """
You are an expert ATS (Applicant Tracking System) compiler and senior technical recruiter.
Your task is to analyze the provided resume text and optionally compare it to the target Job Description (if provided).

Deliver a highly detailed, professional analysis. You must output your response strictly as a JSON object matching the JSON schema below. 
Do not include markdown packaging like ```json ... ``` in your output. Return raw JSON text.

JSON Schema to strictly follow:
{{
  "ats_score": 85, // integer 0-100
  "metrics": [
    {{
      "name": "Layout & Formatting",
      "score": 90, // integer 0-100
      "feedback": "Presents a clean, readable layout, but could benefit from standardizing margins and font hierarchy."
    }},
    {{
      "name": "Grammar & Readability",
      "score": 95,
      "feedback": "No spelling errors detected. Professional and concise vocabulary used."
    }},
    {{
      "name": "Impact & Achievements",
      "score": 70,
      "feedback": "Many bullet points describe tasks rather than quantified outcomes. Use Action verbs + Metrics + Result structure."
    }},
    {{
      "name": "Skills & Keywords",
      "score": 65,
      "feedback": "Missing several critical technical keywords required for modern engineering roles."
    }}
  ],
  "keywords": {{
    "detected": ["React", "Python", "Git", "FastAPI"],
    "missing": ["Docker", "CI/CD", "PostgreSQL", "System Design"]
  }},
  "section_analysis": [
    {{
      "section": "Education",
      "score": 95,
      "comments": "Degree and graduation date clearly listed. Nice layout."
    }},
    {{
      "section": "Work Experience",
      "score": 75,
      "comments": "Good company names, but focus on accomplishments rather than routine responsibilities."
    }},
    {{
      "section": "Projects",
      "score": 80,
      "comments": "Nice project descriptions, but clarify the tech stack used for each project."
    }}
  ],
  "key_strengths": [
    "Strong technical core with React and Python",
    "Professional work history in reputable teams",
    "Clear structure and section headers"
  ],
  "actionable_recommendations": [
    {{
      "issue": "Weak action verbs and lacks metrics",
      "recommendation": "Rewrite resume bullets to start with powerful action verbs and quantify the impact (e.g. increase speed, reduce bugs).",
      "priority": "High",
      "before_after": {{
        "before": "Responsible for maintaining the backend API and fixing bugs.",
        "after": "Optimized database queries and API response times by 35% using FastAPI and PostgreSQL, resolving 15+ critical bugs weekly."
      }}
    }},
    {{
      "issue": "Missing key containerization technologies",
      "recommendation": "If you have experience with Docker or cloud platforms, list them explicitly to bypass automated ATS filters.",
      "priority": "Medium",
      "before_after": {{
        "before": "Ran code on virtual servers.",
        "after": "Containerized the microservices stack using Docker and deployed onto AWS EC2 instances, achieving 99.9% uptime."
      }}
    }}
  ],
  "job_compatibility": {{ // Only fill if Job Description is provided, otherwise return null
    "score": 75, // integer 0-100
    "match_analysis": "The candidate has the core programming skills but lacks experience in database scaling and cloud architectures mentioned in the job description.",
    "skill_gaps": ["Kubernetes", "Redis", "Distributed Systems"]
  }}
}}

Resume Text:
---
{resume_text}
---

Target Job Description (Optional):
---
{job_description}
---
"""

def generate_mock_analysis(resume_text: str, job_description: Optional[str] = None) -> dict:
    """
    Generates a high-quality mock analysis if the Gemini API Key is missing.
    Customizes based on basic content analysis.
    """
    # Simple rule-based mock logic
    resume_lower = resume_text.lower()
    
    detected = []
    for skill in ["python", "react", "javascript", "html", "css", "sql", "git", "docker", "aws", "node"]:
        if skill in resume_lower:
            detected.append(skill.capitalize())
            
    all_possible_missing = ["TypeScript", "CI/CD", "FastAPI", "Kubernetes", "PostgreSQL", "Redis", "GraphQL", "NoSQL", "System Design", "Agile"]
    missing = [s for s in all_possible_missing if s.lower() not in resume_lower][:4]
    if not missing:
        missing = ["Unit Testing", "Microservices"]

    ats_score = 65
    if len(detected) > 3:
        ats_score += 15
    if "education" in resume_lower or "university" in resume_lower or "college" in resume_lower:
        ats_score += 10
    if job_description and len(job_description) > 50:
        ats_score = min(ats_score + 5, 95)
    else:
        ats_score = min(ats_score, 90)

    job_compat = None
    if job_description and len(job_description.strip()) > 10:
        # Check matching words between job desc and resume
        job_lower = job_description.lower()
        gaps = []
        for term in ["kubernetes", "docker", "postgres", "aws", "typescript", "testing", "agile"]:
            if term in job_lower and term not in resume_lower:
                gaps.append(term.capitalize())
        
        match_score = max(40, 100 - len(gaps) * 12)
        job_compat = {
            "score": match_score,
            "match_analysis": f"The resume matches the core technical parameters of the job description. However, we identified {len(gaps)} key skill gaps that are highlighted in the requirements.",
            "skill_gaps": gaps if gaps else ["Specific domain experience"]
        }

    return {
        "ats_score": ats_score,
        "metrics": [
            {
                "name": "Layout & Formatting",
                "score": 85,
                "feedback": "Your layout is well structured. Ensure margins are consistent and bullet points align perfectly."
            },
            {
                "name": "Grammar & Readability",
                "score": 90,
                "feedback": "Great language flow. Keep sentences concise and use active voice rather than passive voice."
            },
            {
                "name": "Impact & Achievements",
                "score": 70,
                "feedback": "Some job descriptions look like lists of daily duties. Start each bullet point with a verb and specify measurable results."
            },
            {
                "name": "Skills & Keywords",
                "score": 75,
                "feedback": f"Detected skills: {', '.join(detected)}. Missing keywords: {', '.join(missing)}."
            }
        ],
        "keywords": {
            "detected": detected if detected else ["General Skills"],
            "missing": missing
        },
        "section_analysis": [
            {
                "section": "Education",
                "score": 90,
                "comments": "Degrees are clearly formatted. Make sure to list graduation year."
            },
            {
                "section": "Work Experience",
                "score": 72,
                "comments": "Good career progression. Focus more on quantification (percentages, dollar amounts, timespans)."
            },
            {
                "section": "Skills Section",
                "score": 80,
                "comments": "Group your skills (e.g. Languages, Frameworks, Tools) to make it easier to read."
            }
        ],
        "key_strengths": [
            "Clear contact details and document hierarchy",
            f"Solid baseline of keywords: {', '.join(detected[:3])}",
            "Strong readability index"
        ],
        "actionable_recommendations": [
            {
                "issue": "Descriptive duties instead of impact-driven accomplishments",
                "recommendation": "Quantify your achievements. Change passive descriptions to action-oriented ones.",
                "priority": "High",
                "before_after": {
                    "before": "Helped manage the developer portal and worked on fixing bugs.",
                    "after": "Collaborated in a team of 4 to resolve 25+ front-end issues weekly, decreasing customer support tickets by 18%."
                }
            },
            {
                "issue": "Missing modern collaborative workflow keywords",
                "recommendation": "Add references to Agile methodologies and CI/CD pipelines to pass recruiters looking for modern engineering practices.",
                "priority": "Medium",
                "before_after": {
                    "before": "Sent code updates to the lead developer.",
                    "after": "Streamlined code deployment workflow using Git, increasing release frequency by implementing automated testing pipelines."
                }
            }
        ],
        "job_compatibility": job_compat
    }

def analyze_resume(resume_text: str, job_description: Optional[str] = None) -> dict:
    """
    Sends the resume and job description to the Gemini model and parses the JSON response.
    Falls back to mock analyzer if API key is missing or calls fail.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.info("Using mock analysis engine (no GEMINI_API_KEY).")
        return generate_mock_analysis(resume_text, job_description)

    try:
        # Prompt build
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            resume_text=resume_text,
            job_description=job_description if job_description else "Not provided"
        )
        
        # Initialize Gemini client
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        result_json = response.text.strip()
        
        # Parse output to ensure validity
        analysis_data = json.loads(result_json)
        return analysis_data
        
    except Exception as e:
        logger.error(f"Gemini API invocation error: {str(e)}. Falling back to mock data.")
        return generate_mock_analysis(resume_text, job_description)
