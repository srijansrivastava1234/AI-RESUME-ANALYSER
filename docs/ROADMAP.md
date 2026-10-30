# Product Development Roadmap — AI Resume Analyser

Development milestones, delivered features, and future architectural initiatives.

---

## Completed Milestones

### Phase 1: Visual PDF Viewer & Recruiter Eye-Tracking Heatmap
- **In-Browser PDF Canvas Renderer**: HTML5 `<canvas>` rendering via `pdfjs-dist` with multi-page navigation and 50%–200% zoom.
- **Layout Extraction Pipeline**: Tokenized bounding box extraction (`[x0, y0, x1, y1]`) classifying text blocks into headers, bullets, and contact rows.
- **Recruiter Scanning Simulation**: Visual density heatmap simulating the 6-second F/Z-pattern recruiter gaze path with layer toggles (Normal PDF, Heatmap, ATS Bounding Boxes).

### Phase 2: Live Job URL Ingestion & Scraping Engine
- **Automated JD Scraper**: Headless ingestion supporting Greenhouse, Lever, LinkedIn, Indeed, and Ashby job postings.
- **Content Normalizer**: Automatic stripping of boilerplate EEO disclaimers, cookie notices, and standard benefits sections.
- **Security Guardrails**: Strict SSRF prevention blocking private RFC 1918 subnets and localhost loopback requests.

### Phase 3: Multi-ATS Simulation Sandbox
- **Engine Simulators**: Deterministic parsers modeling parsing quirks for Workday, Taleo, Greenhouse, iCIMS, Lever, and SAP SuccessFactors.
- **Exploit Guard**: Real-time detection of white-on-white text, micro-fonts (<0.5pt), off-screen DOM shifts, and zero-width characters.

### Phase 4: Universal Multi-Industry & Dynamic Role Readiness
- **16 Multi-Industry Archetypes**: Out-of-the-box competency models across Healthcare, Finance, Marketing, Sales, Operations, HR, Legal, and Design.
- **Dynamic Archetype Synthesis**: On-demand LLM competency generation for custom, emerging, or non-cataloged roles.
- **Dynamic JD N-Gram NLP**: Statistical keyword extraction directly from job descriptions to eliminate hardcoded tech dependencies.

---

## Upcoming Initiatives

- [ ] **Multi-Language OCR Ingestion**: Tesseract / Google Vision OCR pipeline for scanned image-only PDF resumes.
- [ ] **Real-Time Collaborative Editing**: Operational Transformation (OT) / WebSockets for live resume editing and recruiter coaching.
- [ ] **ATS Direct-Apply Webhook**: One-click resume submission via Greenhouse and Lever API integrations.

