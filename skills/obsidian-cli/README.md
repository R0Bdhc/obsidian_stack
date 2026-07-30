# Obsidian CLI Skill

Interact with Obsidian vaults via command-line operations.

## When to Use

- Performing batch operations on vault files
- Checking vault integrity (broken links, orphaned files)
- Managing plugins and themes programmatically
- Automating vault maintenance tasks
- Renaming notes while preserving wikilink integrity

## What It Teaches

This skill teaches how to use the **Obsidian CLI** and related command-line tools to manage vaults at scale.

### Common Operations

#### Check Vault Health

```bash
# Check for broken links
obsidian-cli check-links /path/to/vault

# Find orphaned files (not linked from anywhere)
obsidian-cli find-orphans /path/to/vault

# Vault statistics
obsidian-cli stats /path/to/vault
```

#### Batch Rename with Link Preservation

```bash
# Rename notes matching pattern, update all wikilinks
obsidian-cli rename "Old Prefix-*" "New Prefix-*" /path/to/vault
```

#### Plugin Management

```bash
# List installed plugins
obsidian-cli plugins list /path/to/vault

# Enable/disable plugin
obsidian-cli plugins enable "dataview" /path/to/vault
obsidian-cli plugins disable "templater" /path/to/vault
```

### Vault Maintenance Workflow

1. **Health check** — run `check-links` and `find-orphans`
2. **Clean up** — move orphans to `_Archive/` or delete
3. **Fix links** — batch rename if note titles changed
4. **Update index** — regenerate MOCs and dashboards
5. **Backup** — sync to remote or create snapshot

## Key Conventions

- Always **update wikilinks** when renaming notes
- Use **relative paths** for vault operations
- Test batch operations on a **copy first**
- Respect `.gitignore` and `.obsidian/` settings
