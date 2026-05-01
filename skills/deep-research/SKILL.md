---
name: deep-research
description: Long-form research planning and synthesis framework for industry-chain research, company research, technology moat analysis, competitive landscape, due diligence, and multi-source evidence synthesis. Use when the task needs a structured deep-research plan, source map, evidence grading, contradiction handling, and final research brief. This project-local skill is not a local Gemini API executor and does not provide scripts/research.py.
---

# Deep Research

Use this skill as a long-form research framework inside `产业链投研`. It defines how to plan, collect, grade, and synthesize evidence for complex research tasks.

This skill is not an executable Gemini Deep Research wrapper. There is no local `scripts/research.py`, no bundled `requirements.txt`, and no project-local API runner. Do not try to run missing scripts from this skill.

## When To Use

- Industry-chain structure, value distribution, technology moat, customer verification, and domestic substitution.
- Company or competitor deep dives that need multiple sources and contradiction handling.
- Technical research where the answer depends on process difficulty, yield, reliability, certification, or ecosystem lock-in.
- Due diligence-style synthesis from annual reports, quarterly reports, investor relations, official pages, patents, standards, PDFs, or credible media.
- Research tasks that are too broad for a single source summary but do not require live rumor discovery.

## When Not To Use Alone

- Latest price, market cap, PE/PB, turnover, K-line, earnings release, policy, order, or news facts. Use current data tools or web verification.
- Real-time AI-chain rumors, X/Twitter leads, Grok, or Gemini webpage collection. Use `ai-chain-research-orchestrator` and `browser-grok-gemini-research`.
- Final stock ranking. Use `stock-evaluator`, `business-analyst`, `advanced-evaluation`, and market-data skills after evidence collection.
- Long PDF or report digestion by itself. Use `research-summarizer` to extract claim-evidence-limitations first.

## Workflow

1. Define the research question in one sentence.
2. Split the question into sub-questions:
   - Industry-chain position
   - Value share and profit pool
   - Technology or process moat
   - Customer verification and switching cost
   - Global leaders and competitive structure
   - Domestic substitution difficulty
   - Stock mapping, if relevant
3. Build a source plan:
   - Use `search-specialist` for query design and official-source priority.
   - Use `web-scraper`, `firecrawl-scraper`, or `tavily-web` for extraction when needed.
   - Use `research-summarizer` for long reports, whitepapers, transcripts, PDFs, or multi-source briefs.
4. Grade evidence:
   - A: official filings, exchange disclosures, company announcements, prospectuses, annual or quarterly reports.
   - B: customer/supplier official pages, standards bodies, patents, industry associations, credible trade publications.
   - C: reputable financial media or data vendors.
   - D: X/Twitter, forums, blogs, and model-generated summaries; treat as leads only.
5. Synthesize:
   - Separate confirmed facts, plausible leads, contradictions, and unresolved gaps.
   - Separate industry strength, fundamental quality, earnings elasticity, and trading elasticity.
   - Keep missing or unverifiable numbers as `N/A`.

## Gemini Web Deep Research

If the user explicitly asks to use Gemini web Deep Research, this skill only provides the research structure. Use `browser-grok-gemini-research` for the browser workflow, then bring the collected output back here for evidence grading and synthesis.

## Output

Use conclusion-first structure:

```text
结论先行：一句话回答

证据分层：
- A类硬证据：
- B类辅助证据：
- C类参考证据：
- 待验证线索：

产业链判断：
- 位置：
- 价值量：
- 壁垒：
- 全球龙头：
- 国产替代难度：

个股映射：
- 真受益：
- 弱相关：
- 蹭概念：

后续跟踪：
- 官方数据：
- 订单/客户：
- 价格/产能：
- 行情/估值：
```
