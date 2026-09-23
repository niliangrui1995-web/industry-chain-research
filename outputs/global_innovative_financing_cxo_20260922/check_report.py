from pathlib import Path
import json
import re

path = Path(__file__).resolve().parent / "决策看板_全球创新药融资周期与CXO传导.html"
text = path.read_text(encoding="utf-8")
checks = {
    "utf8": True,
    "bad_tokens": [token for token in ["%s", "None", "nan", "\ufffd"] if (re.search(r"(?<![A-Za-z])" + re.escape(token) + r"(?![A-Za-z])", text, re.I) if token == "nan" else token in text)],
}
checks["tags"] = {tag: len(re.findall(r"<" + tag + r"(?:\s|>)", text, re.I)) for tag in ["html", "head", "body", "section", "table", "tr", "td", "h2"]}
checks["closing"] = {tag: len(re.findall(r"</" + tag + r">", text, re.I)) for tag in ["html", "head", "body", "section", "table", "tr", "td", "h2"]}
ids = re.findall(r'\bid="([^"]+)"', text)
checks["duplicate_ids"] = sorted({value for value in ids if ids.count(value) > 1})
refs = re.findall(r'href="#(evidence-E-\d+)"', text)
targets = re.findall(r'id="(evidence-E-\d+)"', text)
checks["evidence_refs"] = len(refs)
checks["evidence_targets"] = len(targets)
checks["missing_evidence_targets"] = sorted(set(refs) - set(targets))
checks["title_count"] = len(re.findall(r"<h2>", text, re.I))
print(json.dumps(checks, ensure_ascii=False, indent=2))
if checks["bad_tokens"] or checks["duplicate_ids"] or checks["missing_evidence_targets"]:
    raise SystemExit(2)
for tag in ["html", "head", "body", "section", "table", "tr", "td", "h2"]:
    if checks["tags"][tag] != checks["closing"][tag]:
        raise SystemExit(3)
