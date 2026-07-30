#!/usr/bin/env python3
"""知识深度生成器 v2 — 从 JSON 数据文件读取并写入 Knowledge/ 文章"""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
BASE = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE / "idea" / "Knowledge"
DATA_FILE = BASE / "deep_data.json"

def slugify(text: str) -> str:
    import re
    text = re.sub(r'[\\/*?:"<>|\n\r]', "", text)
    return re.sub(r'\s+', " ", text).strip()[:80].replace(" ", "-")

def write_article(domain_dir, topic_name, domain_name, domain_desc, content):
    now = datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    article = f"""---
domain: "{domain_name}"
topic: "{topic_name}"
type: knowledge-article
status: refined
tags:
  - knowledge
  - deep-dive
  - {slugify(domain_name)}
created: {now}
updated: {now}
---

# 📝 {topic_name}

> **领域**: [[索引|{domain_name}]]
> {domain_desc}

---

{content.strip()}

---

## 关联主题

"""
    # Add links to sibling topics
    for other in domain_data["topics"]:
        if other != topic_name:
            article += f"- [[{other}]]\n"

    article += f"""
---
*由 Claude Code 知识精炼器生成 | {now}*
*内容基于专业领域知识综合，不确定处已标注方向*
"""
    (domain_dir / f"{topic_name}.md").write_text(article, encoding="utf-8")

# Main
with open(DATA_FILE, "r", encoding="utf-8") as f:
    all_data = json.load(f)

total = 0
for domain_name, domain_data in all_data.items():
    domain_dir = KNOWLEDGE_DIR / domain_name
    domain_dir.mkdir(parents=True, exist_ok=True)

    # Domain index
    idx = f"""---
domain: "{domain_name}"
type: knowledge-index
status: refined
tags: [knowledge, moc, domain]
created: {datetime.now(CST).strftime("%Y-%m-%d %H:%M")}
---

# 📋 {domain_name} — 知识索引

> {domain_data['desc']}

## 知识点

"""
    for topic_name in domain_data["topics"]:
        idx += f"- [[{topic_name}]]\n"
    idx += "\n---\n*由 Claude Code 知识精炼器生成*\n"
    (domain_dir / "索引.md").write_text(idx, encoding="utf-8")
    print(f"📚 {domain_name}: 索引")

    for topic_name, content in domain_data["topics"].items():
        write_article(domain_dir, topic_name, domain_name, domain_data["desc"], content)
        print(f"  ✓ {topic_name} ({len(content)} chars)")
        total += 1

print(f"\n✅ 共生成 {total} 篇深度知识文章 → {KNOWLEDGE_DIR}")
