#!/usr/bin/env python3
"""Score keyword and requirement overlap between a JD and a resume.

Usage:
    python score_match.py job_description.txt resume.txt
    python score_match.py jd.txt resume.txt --detailed
    python score_match.py jd.txt resume.txt --json

Outputs match scores and keyword overlap analysis.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path


# Common stopwords to filter from keyword extraction
STOPWORDS_EN = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "shall", "you", "your",
    "we", "our", "they", "their", "he", "she", "it", "its", "this", "that",
    "these", "those", "about", "above", "after", "all", "also", "an",
    "any", "as", "just", "not", "so", "if", "no", "very", "too", "only",
    "than", "then", "more", "some", "such", "each", "both", "who", "whom",
    "which", "what", "when", "where", "how", "into", "over", "under",
}

STOPWORDS_ZH = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "所", "为", "所以", "因为", "但是", "然而", "而且", "虽然", "如果",
    "可以", "需要", "应该", "能够", "可能", "已经", "还", "将", "被",
    "把", "让", "对", "从", "与", "及", "或", "并", "而", "且", "中",
    "等", "等等", "之后", "之前", "之后", "以内", "以外", "以上", "以下",
}


def read_file(filepath: str) -> str:
    """Read file with encoding auto-detection."""
    for enc in ["utf-8", "gbk", "gb2312", "gb18030", "latin-1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode {filepath}")


def extract_keywords(text: str, top_n: int = 50) -> list[tuple[str, int]]:
    """Extract meaningful keywords from text, ranked by frequency."""
    # Split into words (handle both Chinese and English)
    # English words
    en_words = re.findall(r"[a-zA-Z+#.]{2,}", text)
    # Chinese bigrams
    zh_chars = re.findall(r"[一-鿿]", text)
    zh_bigrams = [zh_chars[i] + zh_chars[i + 1] for i in range(len(zh_chars) - 1)]

    all_tokens = en_words + zh_bigrams
    filtered = [
        t.lower()
        for t in all_tokens
        if t.lower() not in STOPWORDS_EN and t not in STOPWORDS_ZH
    ]
    return Counter(filtered).most_common(top_n)


def extract_requirements(text: str) -> list[dict]:
    """Extract likely hard requirements from a JD."""
    requirements = []

    # Patterns that signal a requirement
    req_patterns = [
        # Chinese
        re.compile(r"[^\n。]*?(?:要求|必须|需要|具备|熟悉|掌握|精通|了解)[^\n。]*?[。\n]"),
        re.compile(r"[^\n。]*?(?:\d+\s*年\s*(?:以上)?(?:经验|工作经验))[^\n。]*?[。\n]"),
        re.compile(r"[^\n。]*?(?:本科|硕士|博士|学历)[^\n。]*?[。\n]"),
        # English
        re.compile(r"[^\n.]*?(?:require|must|essential|qualification|proficiency)[^\n.]*?[.\n]", re.IGNORECASE),
        re.compile(r"[^\n.]*?(?:\d+\+?\s*years?\s*(?:of\s*)?experience)[^\n.]*?[.\n]", re.IGNORECASE),
    ]

    seen = set()
    for pattern in req_patterns:
        for match in pattern.finditer(text):
            req_text = match.group(0).strip()
            if req_text not in seen and len(req_text) > 5:
                seen.add(req_text)
                requirements.append({
                    "text": req_text,
                    "type": _classify_requirement(req_text),
                })

    return requirements


def _classify_requirement(text: str) -> str:
    """Classify a requirement as hard/soft/education/experience."""
    t = text.lower()
    if any(w in t for w in ("学历", "本科", "硕士", "博士", "degree", "bachelor", "master", "phd")):
        return "education"
    if any(w in t for w in ("年经验", "年工作", "years experience", "years of")):
        return "experience"
    if any(w in t for w in ("沟通", "团队", "领导", "协作", "抗压", "communication", "team", "leader", "collaboration")):
        return "soft_skill"
    return "hard_skill"


def compute_match(jd_text: str, resume_text: str) -> dict:
    """Compute keyword match scores between JD and resume."""
    jd_keywords = dict(extract_keywords(jd_text, top_n=40))
    resume_keywords = dict(extract_keywords(resume_text, top_n=40))
    resume_lower = resume_text.lower()

    # Per-keyword match analysis
    matched = []
    missing = []
    for kw, freq in sorted(jd_keywords.items(), key=lambda x: -x[1]):
        if kw.lower() in resume_lower:
            matched.append({"keyword": kw, "jd_freq": freq})
        else:
            missing.append({"keyword": kw, "jd_freq": freq})

    # Scores
    if not jd_keywords:
        return {"error": "No keywords found in JD"}

    keyword_match_rate = len(matched) / len(jd_keywords)
    weighted_score = sum(m["jd_freq"] for m in matched) / sum(jd_keywords.values()) if jd_keywords else 0

    # Requirements match
    requirements = extract_requirements(jd_text)
    req_matched = 0
    for req in requirements:
        req_words = set(re.findall(r"[a-zA-Z+#.]{2,}|\d+", req["text"]))
        if req_words and any(w.lower() in resume_lower for w in req_words):
            req_matched += 1
    req_match_rate = req_matched / len(requirements) if requirements else 0

    return {
        "total_jd_keywords": len(jd_keywords),
        "matched_keywords": len(matched),
        "missing_keywords": len(missing),
        "keyword_match_rate": round(keyword_match_rate * 100, 1),
        "weighted_match_rate": round(weighted_score * 100, 1),
        "total_requirements": len(requirements),
        "matched_requirements": req_matched,
        "requirement_match_rate": round(req_match_rate * 100, 1),
        "top_matches": matched[:15],
        "top_missing": missing[:15],
        "requirements": requirements,
    }


def format_report(result: dict, detailed: bool = False) -> str:
    """Format the match result as a readable report."""
    if "error" in result:
        return f"Error: {result['error']}"

    lines = [
        "=" * 60,
        "  JD ↔ Resume Match Analysis",
        "=" * 60,
        "",
        f"  关键词匹配率:    {result['keyword_match_rate']}%  ({result['matched_keywords']}/{result['total_jd_keywords']})",
        f"  加权匹配率:      {result['weighted_match_rate']}%  (by JD keyword importance)",
        f"  要求匹配率:      {result['requirement_match_rate']}%  ({result['matched_requirements']}/{result['total_requirements']})",
        "",
        "─" * 60,
        "  ✅ Top Matched Keywords",
        "─" * 60,
    ]

    for m in result["top_matches"]:
        lines.append(f"  + {m['keyword']}  (JD中出现 {m['jd_freq']} 次)")

    lines.extend([
        "",
        "─" * 60,
        "  ❌ Top Missing Keywords (需要补充/强调)",
        "─" * 60,
    ])

    for m in result["top_missing"]:
        lines.append(f"  - {m['keyword']}  (JD中出现 {m['jd_freq']} 次)")

    if detailed and result.get("requirements"):
        lines.extend([
            "",
            "─" * 60,
            "  📋 JD Requirements Check",
            "─" * 60,
        ])
        for i, req in enumerate(result["requirements"], 1):
            lines.append(f"  {i}. [{req['type']}] {req['text'][:100]}")

    lines.extend([
        "",
        "─" * 60,
        "  📊 Overall Assessment",
        "─" * 60,
    ])

    overall = result["weighted_match_rate"]
    if overall >= 70:
        grade = "🟢 Strong Match — 简历与JD高度匹配，可直接投递"
    elif overall >= 45:
        grade = "🟡 Moderate Match — 建议针对缺失关键词调整后再投递"
    else:
        grade = "🔴 Weak Match — 需要重点补充技能或寻找更匹配的岗位"

    lines.append(f"  {grade}")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python score_match.py <jd_file> <resume_file> [--detailed] [--json]")
        print("       python score_match.py --text '<JD text>' '<resume text>'")
        sys.exit(1)

    detailed = "--detailed" in sys.argv
    output_json = "--json" in sys.argv
    direct_text = "--text" in sys.argv

    if direct_text:
        idx = sys.argv.index("--text")
        jd_text = sys.argv[idx + 1]
        resume_text = sys.argv[idx + 2] if len(sys.argv) > idx + 2 else ""
    else:
        jd_file = sys.argv[1]
        resume_file = sys.argv[2]
        jd_text = read_file(jd_file)
        resume_text = read_file(resume_file)

    result = compute_match(jd_text, resume_text)

    if output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result, detailed=detailed))


if __name__ == "__main__":
    main()
