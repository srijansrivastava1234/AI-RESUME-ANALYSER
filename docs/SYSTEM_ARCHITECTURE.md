# System Architecture & Data Flow — AI Resume Analyser

This document provides complete end-to-end architectural schematics, sequence flows, and component interactions for the AI Resume Analyser ecosystem.

---

## 🏗️ High-Level System Architecture

```mermaid
graph TD
    Client[React 19 Frontend Client] -->|Multipart Resume Upload & JD| Gateway[FastAPI Asynchronous Gateway]
    
    subgraph Ingestion & Normalization
        Gateway --> Extractor[PDF / DOCX / TXT Extraction Engine]
        Extractor --> CMap[ISO 19005-2 CMap & Ligature Normalizer]
        CMap --> XYCut[Recursive XY-Cut Layout Linearizer]
    end
    
    subgraph Deterministic Auditing & NLP Core
        XYCut --> PII[NYC LL 144 / EEOC Blind Review PII Redactor]
        PII --> BM25[Okapi BM25+ Keyword Retrieval Engine]
        PII --> Timeline[ISO-8601 Interval Tree Timeline Normalizer]
        PII --> Taxonomy[Ontological Skill Taxonomy & Dilution Guard]
        PII --> Exploit[Adversarial White-Font & Zero-Width Exploit Filter]
    end
    
    subgraph Scoring & Aggregation
        BM25 --> Scoring[4-Pillar Weighted Compliance Calculator]
        Timeline --> Scoring
        Taxonomy --> Scoring
        Exploit --> Scoring
        Scoring --> Grade[Letter Grade A+ to D & Remediation Matrix]
    end
    
    Grade --> Response[Structured JSON Diagnostic Response]
    Response --> Client
```

---

## 🔄 End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Applicant / Recruiter
    participant UI as React 19 Frontend
    participant API as FastAPI Backend
    participant Parser as PDF / Text Extractor
    participant Engine as ATS Compliance Core
    participant Exporter as PDF Builder Engine

    User->>UI: Upload Resume (PDF) + Job Description
    UI->>API: POST /api/analyze-resume (Multipart Form)
    API->>Parser: Extract raw text streams & font tables
    Parser->>API: Normalized UTF-8 text + Bounding Box Data
    API->>Engine: Run 4-Pillar Audit (Keywords, XYZ, Structure, Density)
    Engine->>API: Compliance Score, Grade, Missing Keywords & Warnings
    API->>UI: JSON Response (<1.5s SLA)
    UI->>User: Interactive ATS Diagnostic Dashboard

    opt Single-Column PDF Export
        User->>UI: Request ATS-Verified PDF
        UI->>API: POST /api/export-ats-pdf
        API->>Exporter: Compile Schema to ATS-Standard PDF
        Exporter->>API: Lossless Single-Column PDF Stream
        API->>UI: Binary PDF Download
        UI->>User: Clean ATS-Verified Resume PDF
    end
```
