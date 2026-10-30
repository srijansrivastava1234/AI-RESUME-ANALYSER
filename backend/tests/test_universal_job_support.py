"""
Test Suite: Universal Multi-Industry Job Title & Dynamic Domain Support
Verifies that the resume analyzer, role readiness engine, keyword matcher,
domain taxonomy, and bullet optimizer work cleanly for ANY job title and industry.
"""

import pytest
from app.role_readiness import evaluate_role_readiness, resolve_role_archetype, generate_dynamic_role_archetype, ROLE_ARCHETYPES
from app.domain_taxonomy import classify_domain
from app.keywords import calculate_keyword_match_score, extract_skills_by_category, extract_dynamic_job_keywords
from app.skill_classifier import audit_skills, classify_single_skill
from app.rewriter import optimize_bullet_heuristic
from app.analyzer import analyze_resume


def test_nursing_role_readiness():
    nursing_resume = """
    Jane Smith, BSN, RN
    Registered Nurse with 5 years of acute care experience.
    Clinical Experience:
    - Administered patient care and triage in high-volume Level 1 trauma emergency department.
    - Expert in IV therapy, catheterization, wound care, and vital signs monitoring.
    - Utilized Epic and Cerner EHR charting systems for 20+ patients per shift.
    - Maintained 100% compliance with HIPAA and infection control protocols.
    Certifications:
    BLS, ACLS, CPR certified. Telemetry trained.
    """
    res = evaluate_role_readiness(nursing_resume, target_role="Registered Nurse")
    assert res["target_role"] == "registered_nurse"
    assert res["readiness_score"] >= 80.0
    assert res["readiness_tier"] in ("Ready", "Strong Candidate")
    assert "patient care" in res["matched_skills"]
    assert "epic" in res["matched_skills"]
    assert "bls" in res["matched_skills"]


def test_accounting_role_readiness():
    accounting_resume = """
    Senior Accountant & Financial Auditor
    - Managed monthly financial reporting, general ledger reconciliation, and journal entries under GAAP and IFRS standards.
    - Prepared corporate tax preparation and supported annual SOX compliance internal audit.
    - Leveraged Excel, QuickBooks, SAP, and NetSuite ERP to automate accounts payable and accounts receivable.
    Certifications:
    CPA Candidate, Financial Modeling certification.
    """
    res = evaluate_role_readiness(accounting_resume, target_role="Senior Accountant")
    assert res["target_role"] == "accountant_auditor"
    assert res["readiness_score"] >= 80.0
    assert "gaap" in res["matched_skills"]
    assert "excel" in res["matched_skills"]
    assert "quickbooks" in res["matched_skills"]


def test_marketing_role_readiness():
    marketing_resume = """
    Digital Marketing Specialist with 4 years scaling SaaS growth.
    - Directed SEO and SEM campaigns generating 40% organic traffic growth.
    - Managed Meta Ads and Google Ads with a 4.2x ROAS and reduced customer acquisition cost (CAC).
    - Analyzed multi-channel funnels using Google Analytics (GA4) and Looker.
    - Automated email marketing drip campaigns in HubSpot and Salesforce CRM.
    """
    res = evaluate_role_readiness(marketing_resume, target_role="Growth Marketer")
    assert res["target_role"] == "digital_marketer"
    assert res["readiness_score"] >= 80.0
    assert "seo" in res["matched_skills"]
    assert "meta ads" in res["matched_skills"]
    assert "hubspot" in res["matched_skills"]


def test_custom_unknown_role_synthesis():
    pilot_resume = """
    Commercial Airline Pilot
    - Logged 4,500 flight hours as First Officer on Boeing 737 passenger aircraft.
    - Conducted pre-flight inspections, flight planning, and cockpit resource management.
    - Maintained 100% compliance with FAA regulations and aviation safety standards.
    """
    # Custom unknown title not in standard taxonomy
    res = evaluate_role_readiness(pilot_resume, target_role="Commercial Airline Pilot")
    assert res["target_role"] == "custom_dynamic_role"
    assert res["role_title"] == "Commercial Airline Pilot"
    assert res["readiness_score"] > 0
    assert "category_breakdown" in res


def test_dynamic_keyword_match_for_non_tech_job():
    resume = """
    Head Chef with extensive culinary background in French cuisine, sous vide cooking, 
    kitchen management, HACCP safety compliance, inventory food cost control, and menu engineering.
    """
    job_description = """
    We are seeking an Executive Chef to oversee kitchen operations.
    Requirements:
    - Mastery of sous vide techniques and high-volume kitchen management.
    - Strict adherence to HACCP food safety protocols.
    - Experience in menu engineering and inventory food cost reduction.
    """
    result = calculate_keyword_match_score(resume, job_description)
    assert result["match_percentage"] >= 50
    assert len(result["matched_keywords"]) > 0


def test_multi_industry_domain_classification():
    nurse_text = "Nurse administering triage, patient care, IV therapy, and vital signs in ICU."
    res_med = classify_domain(nurse_text)
    assert res_med["domain"] == "HEALTHCARE"

    acct_text = "Auditor preparing GAAP financial reporting, general ledger reconciliation, and tax filings."
    res_acct = classify_domain(acct_text)
    assert res_acct["domain"] == "FINANCE_ACCOUNTING"

    mktg_text = "Marketer running SEO, SEM, Meta Ads, and analyzing Google Analytics conversion rate."
    res_mktg = classify_domain(mktg_text)
    assert res_mktg["domain"] == "SALES_MARKETING"


def test_domain_aware_bullet_rewrite():
    nurse_bullet = "helped care for patients during night shifts"
    opt_nurse = optimize_bullet_heuristic(nurse_bullet, target_role="Registered Nurse")
    assert "Spearheaded" in opt_nurse["optimized"]
    assert "patient care" in opt_nurse["optimized"]

    sales_bullet = "helped sell software to enterprise clients"
    opt_sales = optimize_bullet_heuristic(sales_bullet, target_role="Sales Executive")
    assert "pipeline revenue" in opt_sales["optimized"] or "quota" in opt_sales["optimized"]


def test_skill_classifier_non_tech_hard_skills():
    assert classify_single_skill("Patient Care")["type"] == "HARD"
    assert classify_single_skill("GAAP")["type"] == "HARD"
    assert classify_single_skill("SEO")["type"] == "HARD"
    assert classify_single_skill("Supply Chain")["type"] == "HARD"
    assert classify_single_skill("Figma")["type"] == "HARD"
    assert classify_single_skill("Team Player")["type"] == "SOFT"

