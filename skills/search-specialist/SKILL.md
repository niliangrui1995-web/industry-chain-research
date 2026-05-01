---
name: search-specialist
description: Expert source-discovery and verification workflow for industry research, company research, filings, announcements, official pages, PDFs, market data, and conflicting web evidence. Use when a task needs better search queries, source prioritization, cross-checking, contradiction tracking, or a transparent evidence trail before investment synthesis.
---

# Search Specialist

Use this skill as the evidence-discovery layer for `产业链投研`. It improves source finding and verification; it does not make the final industry or stock conclusion.

## Focus Areas

- Advanced search query formulation.
- Official-source discovery for filings, announcements, investor relations pages, exchange disclosures, standards bodies, and industry associations.
- Source quality ranking and contradiction tracking.
- Chinese and English query expansion for global supply-chain research.
- Historical versus current-fact separation.
- Handoff to `research-summarizer`, `web-scraper`, `firecrawl-scraper`, `tavily-web`, or browser Grok/Gemini collection when deeper extraction is needed.

## Source Priority

- First layer: exchange filings, company announcements, annual/interim/quarterly reports, prospectuses, investor relations, official regulator or index pages.
- Second layer: customer/supplier official pages, standards bodies, industry associations, conference papers, patents, and credible trade publications.
- Third layer: reputable financial media and data vendors.
- Fourth layer: X/Twitter, forums, blogs, and model-generated answers. Use these only as leads that need verification.

## Query Families

- Company filings: `company name annual report`, `ticker investor relations`, `公司名 年报`, `公司名 投资者关系`, `公司名 交易所 公告`.
- Supply chain: `company product customer`, `公司名 产品 客户 认证`, `technology supplier qualification`, `segment market share`.
- Technology moat: `yield reliability qualification process`, `良率 可靠性 认证 工艺 参数`.
- Current events: use date windows and exact terms such as `price increase`, `shortage`, `capacity expansion`, `停产`, `涨价`, `缺货`.

## Workflow

1. Define the exact claim to verify or the missing source type.
2. Create 3-5 query variants across Chinese and English when the topic is global.
3. Search broad first, then narrow by official domains, dates, company names, product names, and ticker suffixes.
4. Separate confirmed facts, likely leads, contradictions, and unresolved gaps.
5. Hand dense sources to `research-summarizer` before final synthesis when the evidence set is large.

## Output

- Queries used and why.
- Best sources found with URLs or local paths.
- Source credibility level: official / primary-adjacent / reputable secondary / lead only.
- Confirmed facts, contradictions, and unresolved gaps.
- Recommended next collection step.

For investment research, never treat search rank, marketing language, or model-generated summaries as proof. The final conclusion belongs to `industry-research-router` and the relevant industry or stock skills.
