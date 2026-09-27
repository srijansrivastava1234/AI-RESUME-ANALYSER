# Security Policy & Threat Model — AI Resume Analyser

The **AI Resume Analyser** project prioritizes candidate privacy, zero persistent storage of sensitive Personally Identifiable Information (PII), and defenses against adversarial document injection.

---

## 🔒 Supported Versions

| Version | Supported | Security Patches |
|---|---|---|
| `1.1.x` | ✅ Yes | Actively Supported |
| `1.0.x` | ✅ Yes | Critical Patches Only |
| `< 1.0.0` | ❌ No | Deprecated |

---

## 🛡️ Threat Model & Ingestion Guardrails

### 1. Adversarial White-Font & Zero-Width Injection
- **Threat Vector**: Attackers hide high-frequency keywords or prompt injections (`"Ignore all previous instructions..."`) in zero-point fonts or white text (`#ffffff`).
- **Mitigation**: Pre-scoring filter scans the DOM/PDF text stream for CSS opacity zero, white-on-white text, and zero-width characters (`\u200B`, `\u200C`, `\u200D`, `\uFEFF`), immediately stripping deceptive payloads and penalizing the compliance score.

### 2. PII Sanitization & Data Retention Policy
- **Threat Vector**: Accidental storage or leakage of candidate contact details, addresses, and demographic data.
- **Mitigation**: All incoming resumes are sanitized in-memory using strict regex patterns (`sanitize_pii`). No applicant resume data is persisted to long-term databases or external unvetted APIs.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability within this repository:
1. Please **do not** open a public GitHub issue.
2. Email security findings directly to the repository maintainer with reproduction steps and proof-of-concept payloads.
3. Vulnerabilities will be triaged within 48 hours and patched in an expedited release cycle.
