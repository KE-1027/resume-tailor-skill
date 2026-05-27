# Resume Tailor Skill

Tailor resumes to specific job descriptions — maximize ATS keyword match while maintaining absolute honesty about your experience.

## Installation

### Claude Code
```bash
git clone <repo-url> ~/.claude/skills/resume-tailor-skill
```

### VS Code Copilot
```bash
git clone <repo-url> .github/skills/resume-tailor-skill
```

### Cursor
```bash
git clone <repo-url> .cursor/rules/resume-tailor-skill
```

### Gemini CLI
```bash
git clone <repo-url> ~/.gemini/skills/resume-tailor-skill
```

### Universal (.agents/skills)
```bash
git clone <repo-url> ~/.agents/skills/resume-tailor-skill
```

### Automatic Install
```bash
./install.sh              # Auto-detect platform
./install.sh --platform claude
./install.sh --all
```

## Usage

```
/resume-tailor-skill [paste job description + your resume/background]
```

Or naturally:
```
帮我针对这个岗位要求改一下简历
Tailor my resume for this job
```

## What It Does

1. **Parses the JD** — extracts hard requirements, keywords, role persona
2. **Catalogs your experience** — all skills, experiences, projects with honest proficiency
3. **Matches & maps** — maps every JD requirement to your real experience
4. **Rewrites your resume** — reframes each section with JD-aligned language
5. **Outputs a gap report** — honest assessment of what's missing and how to address it

**No fabrication, no invented experience, no fake metrics.** Only reorganize, rephrase, and highlight.

## Scripts

- `scripts/parse_resume.py` — Parse PDF/DOCX/TXT resumes into structured text
- `scripts/score_match.py` — Calculate JD-resume keyword match percentage

## License

MIT
