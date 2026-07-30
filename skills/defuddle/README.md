# Defuddle Skill

Extract clean Markdown from web pages, removing clutter to save tokens.

## When to Use

- Importing web articles into Obsidian
- Saving documentation for offline reference
- Creating source notes from blog posts
- Extracting content from URLs for research

## What It Teaches

This skill teaches **Defuddle** extraction principles — identifying and preserving main content while removing:

- Navigation menus and sidebars
- Advertisements and popups
- Footer links and legal text
- Comment sections
- Related article widgets
- Social media embeds

## Extraction Workflow

1. **Fetch page** — retrieve HTML from URL
2. **Detect content** — identify main article container
3. **Clean HTML** — remove scripts, styles, non-content elements
4. **Convert to Markdown** — preserve headings, lists, links, code blocks
5. **Add frontmatter** — include title, author, URL, date
6. **Save to vault** — store in appropriate folder (usually `_Inbox/` or `Sources/`)

## Output Format

```markdown
---
title: "Original Article Title"
author: "Author Name"
source: "https://example.com/article"
date: "2026-07-22"
tags: ["source", "web"]
---

# Original Article Title

[Clean content here...]

---
*Extracted from: https://example.com/article*
```

## Key Conventions

- **Preserve structure** — keep headings hierarchy intact
- **Convert relative links** — make absolute or remove
- **Handle images** — download or reference with `![alt](url)`
- **Remove tracking** — strip UTM parameters from URLs
- **Annotate unclear** — mark `[defuddle: unsure]` when extraction is ambiguous
