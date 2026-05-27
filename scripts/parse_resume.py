#!/usr/bin/env python3
"""Parse resume files (PDF, DOCX, TXT) into structured text sections.

Usage:
    python parse_resume.py resume.pdf
    python parse_resume.py resume.docx
    python parse_resume.py resume.txt
    python parse_resume.py resume.pdf --output structured.json

Outputs structured JSON with detected sections:
    {
        "raw_text": "...",
        "sections": {
            "contact": "...",
            "summary": "...",
            "skills": "...",
            "experience": "...",
            "projects": "...",
            "education": "..."
        },
        "skills_found": ["Python", "React", ...],
        "years_experience": {...}
    }
"""

import json
import re
import sys
from pathlib import Path


def read_txt(filepath: str) -> str:
    """Read a plain text file with encoding detection."""
    encodings = ["utf-8", "gbk", "gb2312", "gb18030", "latin-1"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode {filepath} with any common encoding")


def read_pdf(filepath: str) -> str:
    """Extract text from PDF. Tries pdfplumber first, then PyPDF2, then PyMuPDF."""
    # Try pdfplumber (best quality)
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except ImportError:
        pass

    # Try PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        pass

    # Try PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(filepath)
        return "\n".join(page.get_text() for page in doc)
    except ImportError:
        pass

    raise RuntimeError(
        "No PDF library available. Install one: pip install pdfplumber  OR  pip install PyPDF2  OR  pip install PyMuPDF"
    )


def read_docx(filepath: str) -> str:
    """Extract text from DOCX files."""
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        raise RuntimeError(
            "python-docx not installed. Run: pip install python-docx"
        )


def extract_text(filepath: str) -> str:
    """Auto-detect file type and extract raw text."""
    suffix = Path(filepath).suffix.lower()
    if suffix == ".pdf":
        return read_pdf(filepath)
    elif suffix in (".docx", ".doc"):
        return read_docx(filepath)
    elif suffix in (".txt", ".md", ".markdown"):
        return read_txt(filepath)
    else:
        # Try as plain text
        return read_txt(filepath)


def parse_sections(text: str) -> dict:
    """Heuristically split resume text into common sections."""
    sections = {
        "contact": "",
        "summary": "",
        "skills": "",
        "experience": "",
        "projects": "",
        "education": "",
        "other": "",
    }

    # Section header patterns (Chinese + English)
    patterns = {
        "summary": re.compile(
            r"(个人优势|个人简介|自我评价|求职意向|职业目标|"
            r"SUMMARY|OBJECTIVE|PROFILE|PROFESSIONAL\s+SUMMARY)",
            re.IGNORECASE,
        ),
        "skills": re.compile(
            r"(技能|技术栈|专业技能|技术能力|"
            r"SKILLS|TECHNICAL\s+SKILLS|TECHNOLOGIES|TOOLS)",
            re.IGNORECASE,
        ),
        "experience": re.compile(
            r"(工作经历|实习经历|工作经验|实习经验|工作|实习|"
            r"EXPERIENCE|WORK\s+EXPERIENCE|EMPLOYMENT|INTERNSHIP)",
            re.IGNORECASE,
        ),
        "projects": re.compile(
            r"(项目经历|项目经验|项目|"
            r"PROJECTS|PROJECT\s+EXPERIENCE|PORTFOLIO)",
            re.IGNORECASE,
        ),
        "education": re.compile(
            r"(教育背景|教育经历|学历|学校|"
            r"EDUCATION|ACADEMIC)",
            re.IGNORECASE,
        ),
    }

    lines = text.strip().split("\n")
    current_section = "contact"  # Default: first few lines are contact info

    i = 0
    contact_lines = []
    # Collect first portion as contact
    for i, line in enumerate(lines[:15]):
        contact_lines.append(line)
        if any(p.search(line) for p in patterns.values()):
            break
    sections["contact"] = "\n".join(contact_lines)

    # Parse remaining sections
    current = None
    section_lines = {k: [] for k in sections}

    for line in lines[i:]:
        matched = None
        for sec_name, pattern in patterns.items():
            if pattern.search(line.strip()):
                matched = sec_name
                break
        if matched:
            current = matched
            continue
        if current:
            section_lines[current].append(line)
        else:
            section_lines["other"].append(line)

    for key in sections:
        if key != "contact":
            sections[key] = "\n".join(section_lines[key]).strip()

    return sections


def extract_skills(raw_text: str) -> list:
    """Extract common technical skills from text."""
    skill_patterns = [
        # Programming languages
        r"\b(Python|Java|JavaScript|TypeScript|Go|Rust|C\+\+|C#|Ruby|PHP"
        r"|Swift|Kotlin|Scala|R|MATLAB|Dart)\b",
        # Web
        r"\b(HTML|CSS|React|Vue|Angular|Node\.js|Express|Django|Flask"
        r"|Spring|FastAPI|Next\.js|Nuxt|jQuery|Bootstrap|Tailwind)\b",
        # Data & ML
        r"\b(SQL|MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|Spark|Hadoop"
        r"|TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy|Tableau|Power BI)\b",
        # DevOps & Cloud
        r"\b(Docker|Kubernetes|K8s|AWS|Azure|GCP|CI/CD|Jenkins|GitHub Actions"
        r"|Terraform|Ansible|Linux|Nginx|Apache)\b",
        # Tools
        r"\b(Git|GitHub|GitLab|Jira|Confluence|Figma|Sketch|Postman|Swagger)\b",
        # Chinese tech terms
        r"(微服务|分布式|高并发|大数据|人工智能|机器学习|深度学习|数据分析|云计算)",
    ]

    found = set()
    for pattern in skill_patterns:
        for match in re.finditer(pattern, raw_text, re.IGNORECASE):
            found.add(match.group(0))

    return sorted(found)


def estimate_experience_years(text: str) -> dict:
    """Rough estimate of years of experience from resume text."""
    result = {"total_work_years": None, "internships": 0, "roles": []}

    # Look for date ranges like "2020.06 - 2023.07" or "2020-2023"
    date_patterns = [
        re.compile(r"(\d{4})[.\-/年](\d{1,2})?[.\-/月]?\s*[-–—至到]\s*(\d{4})[.\-/年](\d{1,2})?[.\-/月]?"),
        re.compile(r"(\d{4})\s*[-–—]\s*(?:至今|现在|present|now)", re.IGNORECASE),
    ]

    # Find role titles
    role_pattern = re.compile(
        r"(实习生?|工程师|开发|经理|主管|分析师|设计师|INTERN|ENGINEER|DEVELOPER|MANAGER)",
        re.IGNORECASE,
    )
    result["roles"] = list(set(
        m.group(0) for m in role_pattern.finditer(text)
    ))

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_resume.py <resume_file> [--output json]")
        sys.exit(1)

    filepath = sys.argv[1]
    output_json = "--output" in sys.argv

    try:
        raw_text = extract_text(filepath)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    sections = parse_sections(raw_text)
    skills = extract_skills(raw_text)
    exp = estimate_experience_years(raw_text)

    result = {
        "file": filepath,
        "char_count": len(raw_text),
        "raw_text": raw_text,
        "sections": sections,
        "skills_found": skills,
        "skill_count": len(skills),
        "experience_estimate": exp,
    }

    if output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"File: {filepath}")
        print(f"Characters: {len(raw_text)}")
        print(f"Skills detected ({len(skills)}): {', '.join(skills)}")
        print()
        for sec_name, content in sections.items():
            if content.strip():
                print(f"=== {sec_name.upper()} ===")
                print(content[:300])
                if len(content) > 300:
                    print(f"... (+{len(content) - 300} chars)")
                print()


if __name__ == "__main__":
    main()
