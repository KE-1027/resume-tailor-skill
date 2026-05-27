# Resume Tailor Skill / 简历定制技能

> 针对岗位描述（JD）自动定制简历，最大化 ATS 关键词匹配，零造假、只重组真实经历。保留原始排版，直接生成可投递的 DOCX 文件。
>
> JD-targeted resume tailoring — maximize ATS keyword match, zero fabrication. Only reframe real experience. Preserves original formatting, outputs a submission-ready DOCX.

---

## 它能做什么 / What It Does

1. **拆解 JD** — 提取硬性要求、隐性需求、关键词、岗位画像
2. **盘点你的真实经历** — 技能（诚实标注熟练度）、实习、项目、奖项
3. **逐条匹配** — 每条 JD 要求 → 找到你最接近的真实经历 → 标注强匹配/部分匹配/差距
4. **原地改写简历** — 在原始 DOCX 上逐段替换文字，保留字体/字号/表格/颜色不动
5. **差距分析** — 诚实告诉你缺什么、是否致命、怎么补救

**核心铁律：绝不编造经历、技能、数字。** 只会重组、换角度表述、高亮匹配点。

## 安装 / Installation

### Claude Code
```bash
git clone https://github.com/KE-1027/resume-tailor-skill.git ~/.claude/skills/resume-tailor-skill
```

### VS Code Copilot
```bash
git clone https://github.com/KE-1027/resume-tailor-skill.git .github/skills/resume-tailor-skill
```

### Cursor
```bash
git clone https://github.com/KE-1027/resume-tailor-skill.git .cursor/rules/resume-tailor-skill
```

### Gemini CLI
```bash
git clone https://github.com/KE-1027/resume-tailor-skill.git ~/.gemini/skills/resume-tailor-skill
```

### 通用路径 / Universal
```bash
git clone https://github.com/KE-1027/resume-tailor-skill.git ~/.agents/skills/resume-tailor-skill
```

### 自动安装 / Auto Install
```bash
./install.sh              # 自动检测平台
./install.sh --all        # 安装到所有已检测平台
```

## 使用 / Usage

```
/resume-tailor-skill [粘贴 JD] + [粘贴简历或提供文件路径]
/resume-tailor-skill 帮我针对这个岗位改简历
/resume-tailor-skill 针对JD修改，提高匹配度
```

你也直接说人话触发：
```
针对这个岗位要求帮我优化简历
我投了十几个岗都没回音，帮我改下简历
把这段经历按照JD重新写一下
```

## 工作流 / Workflow

```
你的原始简历(DOCX) + 岗位JD
        ↓
   Phase A: JD拆解（硬性要求 + 隐性需求 + 关键词）
        ↓
   Phase B: 候选人能力清单（真实经历全盘点）
        ↓
   Phase C: 逐条匹配（强匹配 / 部分匹配 / 差距）
        ↓
   Phase D: 改写映射（原文 → JD语言，不编造）
        ↓
   Phase E: 生成定制DOCX（保留原始排版） + 匹配报告 + 差距分析
```

## 核心脚本 / Scripts

| 脚本 | 作用 |
|------|------|
| `scripts/rewrite_resume.py` | **核心** — 在原始 DOCX 上逐段替换文字，保留全部格式 |
| `scripts/parse_resume.py` | 从 PDF/DOCX/TXT 提取结构化文本 |
| `scripts/score_match.py` | 计算 JD 与简历的关键词匹配率 |
| `scripts/generate_docx.py` | 从结构化内容生成新 DOCX（无原始文件时的备选方案） |

## 适用场景 / Use Cases

- 海投简历回复率低，需要针对每个岗位定制
- 跨行业/跨岗位投递，同一段经历需要不同角度表述
- 简历关键词命中率不足，被 ATS 自动筛掉
- 不确定自己和岗位的差距在哪里

## 中国市场特别支持

- 中文 JD 解析与中文简历改写
- Boss直聘 / 猎聘 / 智联招聘 / LinkedIn中国 平台策略
- 中英双语简历支持
- 国企 vs 外企 vs 互联网大厂的不同风格适配

## License

MIT
