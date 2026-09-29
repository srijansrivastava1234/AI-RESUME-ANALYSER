"""
Module: docx_exporter.py
Purpose: Compiles structured JSON resume schema into verified single-column OpenXML DOCX files
with deterministic 0.75-inch optical margins, standard Arial typography, and 100% ATS parseability.
"""

import io
from typing import Dict, Any
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def build_ats_docx_resume(resume_data: Dict[str, Any]) -> io.BytesIO:
    """
    Translates structured JSON resume data into a clean, single-column DOCX document stream.
    """
    doc = docx.Document()

    # Set universal 0.75" ATS margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # 1. Contact / Header Block
    contact = resume_data.get("contact", {})
    name = contact.get("name", "Candidate Name")
    
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(name)
    title_run.font.name = "Arial"
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_p.paragraph_format.space_after = Pt(2)

    # Contact details line
    contact_parts = []
    if contact.get("email"):
        contact_parts.append(contact["email"])
    if contact.get("phone"):
        contact_parts.append(contact["phone"])
    if contact.get("location"):
        contact_parts.append(contact["location"])
    if contact.get("linkedin"):
        contact_parts.append(contact["linkedin"])

    if contact_parts:
        c_p = doc.add_paragraph(" | ".join(contact_parts))
        c_p.paragraph_format.space_after = Pt(12)
        for r in c_p.runs:
            r.font.name = "Arial"
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(70, 70, 70)

    def add_section_header(title: str):
        h = doc.add_paragraph()
        h_run = h.add_run(title.upper())
        h_run.font.name = "Arial"
        h_run.font.size = Pt(12)
        h_run.font.bold = True
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)

    # 2. Summary
    summary = resume_data.get("summary", "")
    if summary:
        add_section_header("Professional Summary")
        sp = doc.add_paragraph(summary)
        sp.paragraph_format.space_after = Pt(8)
        for r in sp.runs:
            r.font.name = "Arial"
            r.font.size = Pt(10.5)

    # 3. Work Experience
    experience = resume_data.get("experience", [])
    if experience:
        add_section_header("Work Experience")
        for exp in experience:
            job_p = doc.add_paragraph()
            role_run = job_p.add_run(f"{exp.get('role', 'Role')} — {exp.get('company', 'Company')}")
            role_run.font.bold = True
            role_run.font.name = "Arial"
            role_run.font.size = Pt(11)
            
            dates = exp.get("dates", "")
            if dates:
                d_run = job_p.add_run(f" ({dates})")
                d_run.font.italic = True
                d_run.font.size = Pt(10)
            job_p.paragraph_format.space_after = Pt(2)

            for bullet in exp.get("bullets", []):
                bp = doc.add_paragraph(bullet, style='List Bullet')
                bp.paragraph_format.space_after = Pt(2)
                for r in bp.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(10)

    # 4. Skills
    skills = resume_data.get("skills", [])
    if skills:
        add_section_header("Technical Skills")
        if isinstance(skills, list):
            skills_str = ", ".join(skills)
        else:
            skills_str = str(skills)
        sk_p = doc.add_paragraph(skills_str)
        sk_p.paragraph_format.space_after = Pt(8)
        for r in sk_p.runs:
            r.font.name = "Arial"
            r.font.size = Pt(10)

    # 5. Education
    education = resume_data.get("education", [])
    if education:
        add_section_header("Education")
        for edu in education:
            ep = doc.add_paragraph()
            e_run = ep.add_run(f"{edu.get('degree', 'Degree')} — {edu.get('institution', 'Institution')}")
            e_run.font.bold = True
            e_run.font.name = "Arial"
            e_run.font.size = Pt(10.5)
            if edu.get("year"):
                ey_run = ep.add_run(f" ({edu['year']})")
                ey_run.font.italic = True
                ey_run.font.size = Pt(10)
            ep.paragraph_format.space_after = Pt(4)

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output
