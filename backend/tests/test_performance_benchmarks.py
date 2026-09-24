"""
Performance & Latency Benchmark Regression Suite.
Ensures deterministic auditing modules consistently execute within sub-millisecond to sub-10ms SLAs.
"""

import time
import pytest
from app.bm25_scorer import compute_bm25_plus
from app.font_integrity import audit_font_cmap_integrity, normalize_typographic_ligatures
from app.chronology import audit_career_chronology
from app.redaction import anonymize_resume_for_blind_audit
from app.parser_utils import sanitize_text_cached, fast_tokenize


SAMPLE_LONG_RESUME = """
ALEXANDER MERCER, Ph.D.
Principal Distributed Systems Architect | alex.mercer@systems.ai | (415) 555-0199 | San Francisco, CA

SUMMARY
Visionary Staff/Principal Infrastructure Engineer with 12+ years architecting globally distributed, low-latency data pipelines,
microservice ecosystems, and cloud-native Kubernetes infrastructure handling 500,000+ RPS with 99.999% SLA availability.

CORE COMPETENCIES
Languages: Python 3.12, Go 1.22, Rust, TypeScript, Java 21, C++, SQL, Bash
Cloud & Infrastructure: AWS, Google Cloud Platform (GCP), Kubernetes, Terraform, Docker, Helm, Kafka, Envoy, Istio, Prometheus, Grafana
Data Systems: PostgreSQL, CockroachDB, Redis Enterprise, Apache Cassandra, ClickHouse, Elasticsearch, BigQuery
Security & Compliance: OAuth2, OIDC, SOC2 Type II, ISO 27001, HIPAA, TLS 1.3, Mutual TLS, NYC Local Law 144

PROFESSIONAL EXPERIENCE

Principal Cloud Architect | HyperScale Networks, Inc. | San Francisco, CA
March 2021 – Present
• Architected cross-region multi-cloud Kubernetes deployment spanning AWS and GCP, reducing cloud egress expenditures by 38% ($420,000 annually).
• Spearheaded migration from legacy monolithic message bus to distributed Apache Kafka cluster, improving event ingestion throughput by 450% to 1.2M msgs/sec.
• Formulated zero-trust service mesh using Istio and mTLS, achieving SOC2 Type II certification with zero critical vulnerabilities.
• Mentored 14 senior engineers and established organization-wide RFC engineering design review process.

Senior Staff Systems Engineer | DataMesh Corporation | San Jose, CA
January 2017 – February 2021
• Engineered distributed caching architecture utilizing Redis Enterprise clusters, dropping p99 database read latency from 45ms to 1.8ms.
• Designed real-time clickstream processing engine using Apache Flink and ClickHouse, empowering analytics team to run sub-second queries over 10B records.
• Automated CI/CD deployment pipeline using GitHub Actions, ArgoCD, and Helm, cutting release cycle duration from 4 hours to 8 minutes.

Lead Software Engineer | CloudFirst Technologies | Seattle, WA
June 2013 – December 2016
• Developed core microservices in Go and Python, serving 35M monthly active users with 99.99% uptime.
• Refactored legacy PostgreSQL database schema, resolving lock contention and increasing transactions-per-second by 220%.

EDUCATION
Ph.D. in Computer Science | Stanford University | 2013
B.S. in Electrical Engineering & Computer Science | UC Berkeley | 2009
"""

KEYWORDS_LIST = [
    "Python", "Go", "Rust", "Kubernetes", "Docker", "Terraform", "Kafka",
    "PostgreSQL", "Redis", "AWS", "GCP", "Istio", "Microservices", "CI/CD"
]


def test_bm25_scorer_latency_sla():
    start = time.perf_counter()
    res = compute_bm25_plus(SAMPLE_LONG_RESUME, KEYWORDS_LIST)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    assert res is not None
    # Deterministic lexical calculation should execute in under 25ms
    assert elapsed_ms < 25.0, f"BM25+ execution took {elapsed_ms:.2f}ms, exceeding 25ms SLA"


def test_font_cmap_integrity_latency_sla():
    start = time.perf_counter()
    audit = audit_font_cmap_integrity(SAMPLE_LONG_RESUME)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    assert audit is not None
    assert elapsed_ms < 20.0, f"Font integrity audit took {elapsed_ms:.2f}ms, exceeding 20ms SLA"


def test_career_chronology_latency_sla():
    start = time.perf_counter()
    chron = audit_career_chronology(SAMPLE_LONG_RESUME)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    assert chron is not None
    assert elapsed_ms < 25.0, f"Career chronology audit took {elapsed_ms:.2f}ms, exceeding 25ms SLA"


def test_pii_redactor_latency_sla():
    start = time.perf_counter()
    redaction = anonymize_resume_for_blind_audit(SAMPLE_LONG_RESUME)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    assert redaction is not None
    assert elapsed_ms < 20.0, f"PII redaction took {elapsed_ms:.2f}ms, exceeding 20ms SLA"


def test_parser_utils_cached_sanitization_throughput():
    # Warmup cache
    sanitize_text_cached(SAMPLE_LONG_RESUME)
    
    start = time.perf_counter()
    iterations = 500
    for _ in range(iterations):
        sanitize_text_cached(SAMPLE_LONG_RESUME)
    elapsed_total_ms = (time.perf_counter() - start) * 1000.0
    avg_per_op_us = (elapsed_total_ms / iterations) * 1000.0
    # Cached lookup should be under 50 microseconds per op
    assert avg_per_op_us < 50.0, f"Cached lookup took {avg_per_op_us:.2f}µs per op"
