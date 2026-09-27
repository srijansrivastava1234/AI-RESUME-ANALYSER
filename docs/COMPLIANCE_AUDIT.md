# Algorithmic Bias Audit & Compliance Framework (NYC LL 144 / EU AI Act)

This document specifies the technical and regulatory compliance controls enforced by the **AI Resume Analyser** engine to guarantee non-discriminatory candidate evaluation.

---

## 🏛️ Regulatory Standards Enforced

### 1. New York City Local Law 144 (NYC LL 144)
- **Requirement**: Automated Employment Decision Tools (AEDT) must undergo independent annual bias audits for sex, race, and ethnicity selection rates.
- **Implementation**:
  - Deterministic PII scrub removing full candidate names, contact information, and geographic location before NLP evaluation.
  - Zero-storage policy for raw identifiable applicant data.

### 2. EU AI Act (Article 10 & High-Risk AI Classification)
- **Requirement**: AI systems used in recruitment and human resources are classified as high-risk, requiring continuous bias risk assessments, explainable score calculations, and auditable scoring factors.
- **Implementation**:
  - Mathematical transparency: composite score is directly derivable from 4 deterministic sub-scores.
  - No black-box automated rejections: all feedback provides actionable remediation guidance.

### 3. EEOC Title VII & ADEA Age Discrimination Guard
- **Requirement**: Prohibition against employment discrimination based on age, race, color, religion, sex, or national origin.
- **Implementation**:
  - Date normalization scrubs high school / early undergraduate graduation years exceeding a 10-year threshold to eliminate age-estimation proxy markers.

---

## 🛡️ Compliance Verification Matrix

| Regulation | Target Metric | System Control | Enforcement Module |
|---|---|---|---|
| **NYC LL 144 § 20-871** | Impact Ratio $\ge 0.80$ | Anonymous Candidate Hashing | `backend/app/compliance.py` |
| **EU AI Act Art. 10(2)** | 100% Explainability | Deterministic Heuristic Weights | `backend/app/scoring.py` |
| **ADEA (29 U.S.C. § 623)** | Zero Graduation Age Proxy | Education Year Normalization | `backend/app/date_normalizer.py` |
| **GDPR Art. 17 (Right to Erasure)** | Ephemeral Processing | Stateless In-Memory Ingestion | `backend/app/main.py` |
