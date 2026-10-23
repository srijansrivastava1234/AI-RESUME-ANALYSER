# Security Policy & Threat Model — AI Resume Analyser

The **AI Resume Analyser** project prioritizes candidate privacy, zero persistent storage of sensitive Personally Identifiable Information (PII), and defenses against adversarial document injection.

---

## 🔒 Supported Versions

| Version | Supported | Security Patches |
|---|---|---|
| `3.7.x` | ✅ Yes | Current Flagship Release |
| `3.x`   | ✅ Yes | Actively Supported |
| `2.x`   | ⚠️ Limited | Security Patches Only |
| `< 2.0.0` | ❌ No | Deprecated |

---

## 🛡️ Threat Model & Ingestion Guardrails

### 1. Adversarial White-Font, Steganography & Prompt Injection
- **Threat Vector**: Attackers hide high-frequency keywords, zero-width Unicode characters (`\u200B`, `\u200C`, `\u200D`, `\uFEFF`), or prompt injections (`"Ignore all previous instructions..."`) to manipulate downstream LLM scoring.
- **Mitigation**: Integrated text-stream normalization and `audit_prompt_injection_safety` scan incoming resumes prior to LLM compilation, stripping invisible characters and flagging adversarial jailbreak attempts.

### 2. SSRF Protection on External Ingestion
- **Threat Vector**: Malicious job posting URLs or redirect chains targeting cloud metadata services (`169.254.169.254`) or loopback/private network ranges.
- **Mitigation**: Pre-request DNS resolution checks and per-hop redirect re-validation block all non-routable, private, multicast, and loopback IP spaces with a strict redirect cap.

### 3. Memory & DoS Ingestion Limits
- **Threat Vector**: Extremely large multipart payloads causing worker out-of-memory crashes.
- **Mitigation**: Strict stream-seek size verification (10MB maximum payload budget) enforced prior to reading payloads into memory across all ingestion endpoints.

### 4. PII Sanitization & Data Retention Policy
- **Threat Vector**: Accidental storage or leakage of candidate contact details, addresses, and demographic data.
- **Mitigation**: All incoming resumes are sanitized in-memory using strict regex patterns (`sanitize_pii`). No applicant resume data is persisted to long-term databases or external unvetted APIs.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability within this repository:
1. Please **do not** open a public GitHub issue.
2. Email security findings directly to the repository maintainer with reproduction steps and proof-of-concept payloads.
3. Vulnerabilities will be triaged within 48 hours and patched in an expedited release cycle.
