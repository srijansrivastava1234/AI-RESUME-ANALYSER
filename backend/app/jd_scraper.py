import re
import socket
import ipaddress
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("JDScraper")

# Common technical skill terms to recognize from JD text
COMMON_TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Vue", "Angular",
    "FastAPI", "Django", "Flask", "Go", "Golang", "Rust", "Java", "Spring Boot",
    "C++", "C#", ".NET", "PHP", "Ruby", "Ruby on Rails", "SQL", "PostgreSQL",
    "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "DynamoDB",
    "AWS", "Amazon Web Services", "GCP", "Google Cloud", "Azure", "Docker",
    "Kubernetes", "Terraform", "Ansible", "CI/CD", "Git", "GitHub Actions",
    "GraphQL", "REST API", "Microservices", "Kafka", "RabbitMQ", "Spark",
    "Hadoop", "Airflow", "Pandas", "NumPy", "Scikit-Learn", "PyTorch", "TensorFlow",
    "Linux", "OAuth", "JWT", "Prometheus", "Grafana", "TailwindCSS", "Next.js"
]

BOILERPLATE_PATTERNS = [
    r'(?i)equal\s+opportunity\s+employer(?:\s+statement)?.*',
    r'(?i)we\s+(?:are\s+proud\s+to\s+be\s+an|celebrate)\s+equal\s+opportunity.*',
    r'(?i)we\s+do\s+not\s+discriminate\s+on\s+the\s+basis\s+of\s+(?:race|color|religion|gender|sex|sexual\s+orientation).*',
    r'(?i)all\s+qualified\s+applicants\s+will\s+receive\s+consideration\s+for\s+employment\s+without\s+regard\s+to.*',
    r'(?i)by\s+submitting\s+your\s+application,\s+you\s+agree\s+to\s+our\s+privacy\s+policy.*',
    r'(?i)we\s+use\s+cookies\s+to\s+(?:enhance|improve)\s+your\s+browsing\s+experience.*',
    r'(?i)applicant\s+privacy\s+(?:notice|policy).*',
    r'(?i)accommodations\s+for\s+applicants\s+with\s+disabilities.*'
]

def validate_url_security(target_url: str) -> None:
    """
    Guards against Server-Side Request Forgery (SSRF) and malicious scheme injection.
    Ensures target URL uses http/https and does NOT resolve to private, loopback,
    link-local, or reserved network addresses.
    """
    if not target_url or not isinstance(target_url, str):
        raise ValueError("Invalid target URL provided.")

    parsed = urlparse(target_url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must contain a valid hostname.")

    # Check for localhost literal
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        raise ValueError("Access to loopback or local host addresses is prohibited.")

    # Resolve IP addresses and verify they are strictly public
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for entry in addr_info:
            ip_str = entry[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
                raise ValueError(f"Access to private or internal IP range ({ip_str}) is blocked for security.")
    except socket.gaierror as e:
        raise ValueError(f"Unable to resolve hostname '{hostname}': {str(e)}")


def clean_job_text(raw_text: str) -> str:
    """
    Cleans and strips boilerplate EEO and legal notices from extracted job text.
    """
    if not raw_text:
        return ""

    text = raw_text
    for pat in BOILERPLATE_PATTERNS:
        text = re.sub(pat, '', text)

    # Normalize whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = '\n'.join(lines)
    # Remove excessive blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts high-priority tech skills from cleaned job description text.
    """
    found_skills = []
    text_lower = f" {text.lower()} "

    for skill in COMMON_TECH_SKILLS:
        # Regex word boundary match
        escaped = re.escape(skill.lower())
        pattern = r'(?<![a-zA-Z0-9_])' + escaped + r'(?![a-zA-Z0-9_])'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def parse_job_html(html_content: str, url: str) -> Dict[str, Any]:
    """
    Parses HTML content using specialized selectors for major job boards or generic fallback.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove non-content elements
    for element in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "iframe"]):
        element.decompose()

    domain = urlparse(url).netloc.lower()
    job_title = ""
    company = ""
    main_text = ""

    # 1. Greenhouse
    if "greenhouse.io" in domain:
        title_el = soup.find(class_=re.compile(r'app-title|job-title', re.I)) or soup.find("h1")
        if title_el:
            job_title = title_el.get_text(strip=True)
        company_el = soup.find(class_=re.compile(r'company-name', re.I))
        if company_el:
            company = company_el.get_text(strip=True)
        content_el = soup.find(id="content") or soup.find(class_=re.compile(r'job-description|content', re.I))
        if content_el:
            main_text = content_el.get_text(separator="\n")

    # 2. Lever
    elif "lever.co" in domain:
        title_el = soup.find(class_=re.compile(r'posting-headline', re.I)) or soup.find("h2") or soup.find("h1")
        if title_el:
            job_title = title_el.get_text(strip=True)
        content_el = soup.find(class_=re.compile(r'posting-description|section-wrapper', re.I)) or soup.find("div", class_="content")
        if content_el:
            main_text = content_el.get_text(separator="\n")

    # 3. Ashby
    elif "ashbyhq.com" in domain:
        title_el = soup.find("h1")
        if title_el:
            job_title = title_el.get_text(strip=True)
        content_el = soup.find(attrs={"data-qa": "job-description"}) or soup.find("main")
        if content_el:
            main_text = content_el.get_text(separator="\n")

    # 4. Workable
    elif "workable.com" in domain:
        title_el = soup.find("h1")
        if title_el:
            job_title = title_el.get_text(strip=True)
        content_el = soup.find(attrs={"data-ui": "job-description"}) or soup.find("main")
        if content_el:
            main_text = content_el.get_text(separator="\n")

    # 5. LinkedIn
    elif "linkedin.com" in domain:
        title_el = soup.find(class_=re.compile(r'top-card-layout__title|job-title', re.I)) or soup.find("h1")
        if title_el:
            job_title = title_el.get_text(strip=True)
        company_el = soup.find(class_=re.compile(r'topcard__org-name-link|company-name', re.I))
        if company_el:
            company = company_el.get_text(strip=True)
        content_el = soup.find(class_=re.compile(r'show-more-less-html__markup|description__text', re.I))
        if content_el:
            main_text = content_el.get_text(separator="\n")

    # 6. Indeed
    elif "indeed.com" in domain:
        title_el = soup.find(id="jobsearch-JobInfoHeader-title") or soup.find("h1")
        if title_el:
            job_title = title_el.get_text(strip=True)
        content_el = soup.find(id="jobDescriptionText") or soup.find(class_="jobsearch-jobDescriptionText")
        if content_el:
            main_text = content_el.get_text(separator="\n")

    # 7. Generic Fallback
    if not main_text:
        # Try finding article, main, or primary content block
        candidates = soup.find_all(["article", "main", "div", "section"], class_=re.compile(r'job|description|posting|career|vacancy|details', re.I))
        if candidates:
            # Pick candidate with most text
            best_candidate = max(candidates, key=lambda el: len(el.get_text()))
            if len(best_candidate.get_text()) >= 150:
                main_text = best_candidate.get_text(separator="\n")

        if not main_text:
            body = soup.find("body")
            main_text = body.get_text(separator="\n") if body else soup.get_text(separator="\n")

    # Fallback title if not yet extracted
    if not job_title:
        h1_tag = soup.find("h1")
        if h1_tag:
            job_title = h1_tag.get_text(strip=True)
        else:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                job_title = og_title["content"].strip()
            else:
                title_tag = soup.find("title")
                if title_tag:
                    raw_t = title_tag.get_text(strip=True)
                    # Split away " - Company" or " | Company"
                    job_title = re.split(r'\s+[-|–—]\s+', raw_t)[0].strip()


    # Clean description
    cleaned_desc = clean_job_text(main_text)
    extracted_skills = extract_skills_from_text(cleaned_desc)
    word_count = len(cleaned_desc.split())

    return {
        "success": True,
        "url": url,
        "domain": domain,
        "job_title": job_title or "Target Role",
        "company": company or "Target Company",
        "cleaned_description": cleaned_desc,
        "word_count": word_count,
        "extracted_skills": extracted_skills,
        "warnings": [] if word_count >= 50 else ["The extracted job description appears unusually short. You may paste additional requirements manually."]
    }


async def scrape_job_description(target_url: str) -> Dict[str, Any]:
    """
    Fetches and sanitizes job descriptions from external URLs asynchronously.
    """
    validate_url_security(target_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache"
    }

    async with httpx.AsyncClient(timeout=12.0, follow_redirects=True, headers=headers) as client:
        try:
            response = await client.get(target_url.strip())
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Target job page returned HTTP {response.status_code} ({response.reason_phrase}).",
                    "url": target_url
                }

            html_content = response.text
            if not html_content or len(html_content.strip()) < 50:
                return {
                    "success": False,
                    "error": "The job posting page returned an empty or unreadable HTML document.",
                    "url": target_url
                }

            result = parse_job_html(html_content, target_url)
            return result

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request to target job page timed out after 12 seconds. Please check the URL or paste the job description manually.",
                "url": target_url
            }
        except httpx.RequestError as req_err:
            return {
                "success": False,
                "error": f"Failed to connect to job page: {str(req_err)}",
                "url": target_url
            }
