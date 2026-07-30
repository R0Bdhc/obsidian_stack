# Obsidian Markdown Skill

Create and edit Obsidian Flavored Markdown (OFM) files.

## When to Use

- Creating or editing `.md` files in an Obsidian vault
- User mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes
- Need to ensure proper Obsidian-specific syntax instead of generic Markdown

## What It Teaches

This skill teaches **Obsidian Flavored Markdown (OFM)**, which extends CommonMark and GitHub Flavored Markdown with Obsidian-specific syntax:

### Wikilinks

Internal vault links using `[[...]]` syntax:

```markdown
[[Note Name]]
[[Note Name|display text]]
[[Note Name#Heading]]
```

**Why**: Obsidian tracks renames automatically and builds the graph view from wikilinks. Standard `[text](path)` links break backlink functionality.

### Embeds

Embed content from other notes or images:

```markdown
![[Image.png]]
![[Other Note]]
![[Other Note#Section]]
```

### Callouts

Highlighted information blocks:

```markdown
> [!NOTE] Title
> Content here

> [!WARNING]
> Important warning

> [!TIP]
> Helpful tip

> [!INFO]
> Informational note
```

Supported types: `NOTE`, `WARNING`, `TIP`, `INFO`, `DANGER`, `SUCCESS`, `QUESTION`, `QUOTE`

### Properties / Frontmatter

YAML frontmatter at the top of the note:

```yaml
---
title: "Note Title"
tags:
  - tag1
  - tag2
aliases:
  - Alternative Name
created: 2026-07-22
---
```

### Tags

Inline tags and frontmatter tags:

```markdown
#tag #tag-with-spaces
```

### Dataview Inline Fields

```markdown
field:: value
```

## Workflow: Creating an Obsidian Note

1. **Add frontmatter** with properties (title, tags, aliases) at the top
2. **Write content** using standard Markdown plus Obsidian-specific syntax
3. **Link related notes** using `[[wikilinks]]` for internal connections
4. **Embed content** from other notes/images using `![[embed]]` syntax
5. **Add callouts** for highlighted information using `> [!type]` syntax
6. **Verify** the note renders correctly in Obsidian's reading view

## Key Conventions

- **Internal links**: Always use `[[wikilinks]]` for notes within the vault
- **External links**: Use standard `[text](url)` Markdown links for external URLs only
- Without this skill, agents often generate standard Markdown links that break Obsidian's graph view and backlink functionality
