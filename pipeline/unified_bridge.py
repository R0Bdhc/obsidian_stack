#!/usr/bin/env python3
"""
Unified Bridge - Core ingestion engine for unified-obsidian-knowledge
Combines Whisper transcription, LLM enhancement, and Obsidian formatting.
"""

import os
import sys
import json
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import yaml

# ───────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "workflow.yaml")

DEFAULT_CONFIG = {
    "vault_path": "/path/to/Your-Obsidian-Vault",
    "inbox_folder": "_Inbox",
    "processing_folder": "_Processing",
    "archive_folder": "_Archive",
    "whisper": {
        "model": "medium",
        "language": "zh",
        "device": "auto"  # auto, cpu, cuda
    },
    "llm": {
        "enabled": True,
        "endpoint": "http://localhost:3000/api/chat/completions",
        "api_key": "",
        "model": "llama3.1:8b",
        "temperature": 0.3
    },
    "frontmatter": {
        "auto_tag": True,
        "auto_summary": True,
        "required_fields": ["title", "date", "tags", "status"]
    },
    "templates": {
        "inbox": "templates/inbox-note.md",
        "concept": "templates/concept-note.md",
        "source": "templates/source-note.md",
        "daily": "templates/daily-note.md"
    }
}


def load_config() -> Dict:
    """Load configuration from YAML or return defaults."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            # Merge with defaults for missing keys
            merged = DEFAULT_CONFIG.copy()
            merged.update(config)
            return merged
    return DEFAULT_CONFIG


# ───────────────────────────────────────────
# File System Helpers
# ───────────────────────────────────────────

def ensure_dir(path: str) -> str:
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_inbox_path(config: Dict) -> str:
    vault = config["vault_path"]
    inbox = config["inbox_folder"]
    month_folder = datetime.now().strftime("%Y-%m")
    path = os.path.join(vault, inbox, month_folder)
    return ensure_dir(path)


def safe_filename(title: str) -> str:
    """Create filesystem-safe filename."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    cleaned = re.sub(r'\s+', "-", cleaned)
    return cleaned or "untitled"


# ───────────────────────────────────────────
# Whisper Integration
# ───────────────────────────────────────────

def transcribe_audio(audio_path: str, config: Dict) -> str:
    """Transcribe audio using local Whisper."""
    whisper_cfg = config["whisper"]
    model = whisper_cfg.get("model", "medium")
    language = whisper_cfg.get("language", "zh")
    device = whisper_cfg.get("device", "auto")

    print(f"🎙️  Transcribing with Whisper ({model})...")

    cmd = [
        "whisper",
        audio_path,
        "--model", model,
        "--language", language,
        "--output_format", "txt",
        "--output_dir", tempfile.gettempdir()
    ]

    if device != "auto":
        cmd.extend(["--device", device])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        transcript_path = os.path.join(tempfile.gettempdir(), f"{base_name}.txt")

        if os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        else:
            raise FileNotFoundError(f"Transcript not found at {transcript_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Whisper error: {e.stderr}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print("❌ Whisper not found. Install with: pip install openai-whisper", file=sys.stderr)
        raise


# ───────────────────────────────────────────
# LLM Enhancement (Open WebUI)
# ───────────────────────────────────────────

def call_local_llm(prompt: str, config: Dict) -> Optional[str]:
    """Call local LLM via Open WebUI API."""
    llm_cfg = config.get("llm", {})
    if not llm_cfg.get("enabled", False):
        return None

    endpoint = llm_cfg.get("endpoint", "")
    api_key = llm_cfg.get("api_key", "")
    model = llm_cfg.get("model", "llama3.1:8b")
    temperature = llm_cfg.get("temperature", 0.3)

    if not endpoint:
        return None

    try:
        import requests

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "stream": False
        }

        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        return None

    except Exception as e:
        print(f"⚠️  LLM enhancement failed: {e}", file=sys.stderr)
        return None


def generate_frontmatter_llm(title: str, content: str, config: Dict) -> Dict:
    """Use LLM to generate intelligent frontmatter."""
    prompt = f"""Analyze the following note and generate JSON frontmatter metadata.

Title: {title}
Content preview: {content[:1500]}...

Respond ONLY with a JSON object containing these fields:
- "summary": A one-sentence summary (max 20 words)
- "tags": Array of 3-7 relevant tags (lowercase, kebab-case)
- "category": One of [concept, project, source, person, daily, idea]
- "priority": One of [low, medium, high]

JSON:"""

    response = call_local_llm(prompt, config)
    if response:
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback to basic frontmatter
    return {
        "summary": f"Notes on {title}",
        "tags": ["inbox"],
        "category": "idea",
        "priority": "medium"
    }


# ───────────────────────────────────────────
# Note Formatting
# ───────────────────────────────────────────

def load_template(template_name: str, config: Dict) -> str:
    """Load a note template."""
    vault = config["vault_path"]
    template_path = config.get("templates", {}).get(template_name)

    if template_path:
        full_path = os.path.join(vault, template_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()

    # Default templates
    templates = {
        "inbox": """---
title: "{{title}}"
date: "{{date}}"
time: "{{time}}"
source_type: "{{source_type}}"
status: "inbox"
tags: {{tags}}
category: "{{category}}"
priority: "{{priority}}"
summary: "{{summary}}"
word_count: {{word_count}}
---

# {{title}}

> 自动录入：{{date}} {{time}} | 来源：{{source_type}} | 状态：🟡 inbox

## 原始内容

{{content}}

## 待处理

- [ ] 提炼核心概念
- [ ] 添加相关链接 [[...]]
- [ ] 确认归档位置（Concepts/Projects/Sources/People）

## 关联笔记

-
""",
        "concept": """---
title: "{{title}}"
date: "{{date}}"
tags: {{tags}}
category: "concept"
status: "refined"
---

# {{title}}

{{content}}

## 定义

## 关键要点

## 关联概念

- [[...]]

## 来源

- [[...]]
""",
        "source": """---
title: "{{title}}"
date: "{{date}}"
tags: {{tags}}
category: "source"
source_type: "{{source_type}}"
status: "refined"
---

# {{title}}

## 元数据

- 作者：
- 来源：{{source_type}}
- 日期：{{date}}

## 笔记

{{content}}

## 关键概念

- [[...]]

## 我的思考

"""
    }
    return templates.get(template_name, templates["inbox"])


def format_note(
    title: str,
    content: str,
    source_type: str = "text",
    template: str = "inbox",
    config: Optional[Dict] = None
) -> str:
    """Format content into an Obsidian-ready note."""
    if config is None:
        config = load_config()

    now = datetime.now()
    llm_data = generate_frontmatter_llm(title, content, config)

    # Build frontmatter data
    data = {
        "title": title,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "source_type": source_type,
        "tags": json.dumps(llm_data.get("tags", ["inbox"]), ensure_ascii=False),
        "category": llm_data.get("category", "idea"),
        "priority": llm_data.get("priority", "medium"),
        "summary": llm_data.get("summary", f"Notes on {title}"),
        "word_count": len(content.split()),
        "content": content
    }

    # Load and render template
    template_str = load_template(template, config)
    for key, value in data.items():
        template_str = template_str.replace(f"{{{{{key}}}}}", str(value))

    return template_str


# ───────────────────────────────────────────
# Main Operations
# ───────────────────────────────────────────

def ingest_voice(audio_path: str, title: Optional[str] = None, config: Optional[Dict] = None) -> Dict:
    """Ingest voice file: transcribe and create note."""
    if config is None:
        config = load_config()

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    note_title = title or safe_filename(os.path.splitext(os.path.basename(audio_path))[0])
    transcript = transcribe_audio(audio_path, config)

    note_content = format_note(note_title, transcript, source_type="voice", config=config)
    inbox = get_inbox_path(config)
    note_path = os.path.join(inbox, f"{datetime.now().strftime('%Y%m%d')}-{safe_filename(note_title)}.md")

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    return {
        "note_path": note_path,
        "transcription": transcript,
        "word_count": len(transcript.split()),
        "title": note_title
    }


def ingest_text(text_path: str, title: Optional[str] = None, tags: Optional[List[str]] = None, config: Optional[Dict] = None) -> Dict:
    """Ingest text file."""
    if config is None:
        config = load_config()

    with open(text_path, "r", encoding="utf-8") as f:
        content = f.read()

    note_title = title or safe_filename(os.path.splitext(os.path.basename(text_path))[0])
    note_content = format_note(note_title, content, source_type="text", config=config)

    # Inject custom tags if provided
    if tags:
        tag_line = f"tags: {json.dumps(tags, ensure_ascii=False)}"
        note_content = re.sub(r'tags: .*', tag_line, note_content)

    inbox = get_inbox_path(config)
    note_path = os.path.join(inbox, f"{datetime.now().strftime('%Y%m%d')}-{safe_filename(note_title)}.md")

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    return {"note_path": note_path, "title": note_title}


def ingest_web(url: str, title: Optional[str] = None, config: Optional[Dict] = None) -> Dict:
    """Ingest web content (uses defuddle or basic extraction)."""
    if config is None:
        config = load_config()

    try:
        import requests
        from urllib.parse import urlparse

        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        # Basic HTML to text (fallback; ideally use defuddle)
        html = response.text
        text = re.sub(r'<[^>]+>', '', html)  # Strip tags (very basic)
        text = re.sub(r'\n\s*\n+', '\n\n', text)  # Normalize whitespace

        note_title = title or safe_filename(urlparse(url).netloc)
        note_content = format_note(note_title, text, source_type="web", config=config)

        inbox = get_inbox_path(config)
        note_path = os.path.join(inbox, f"{datetime.now().strftime('%Y%m%d')}-{safe_filename(note_title)}.md")

        with open(note_path, "w", encoding="utf-8") as f:
            f.write(note_content)

        # Extract links
        links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)

        return {
            "note_path": note_path,
            "title": note_title,
            "extracted_links": list(set(links))[:20]
        }

    except ImportError:
        raise RuntimeError("requests library required for web ingestion. Install: pip install requests")


def batch_ingest(watch_dir: str, auto_archive: bool = True, config: Optional[Dict] = None) -> Dict:
    """Process all supported files in a directory."""
    if config is None:
        config = load_config()

    supported = {".mp3", ".wav", ".m4a", ".ogg", ".txt", ".md"}
    processed = []
    failed = []

    watch_path = Path(watch_dir)
    if not watch_path.exists():
        return {"processed_count": 0, "failed_files": [], "error": f"Directory not found: {watch_dir}"}

    for file_path in watch_path.iterdir():
        if file_path.suffix.lower() not in supported:
            continue

        try:
            if file_path.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg"}:
                result = ingest_voice(str(file_path), config=config)
            else:
                result = ingest_text(str(file_path), config=config)

            processed.append(result)

            if auto_archive:
                archive_dir = Path(watch_dir) / ".processed"
                archive_dir.mkdir(exist_ok=True)
                file_path.rename(archive_dir / f"{datetime.now().strftime('%Y%m%d-%H%M')}-{file_path.name}")

        except Exception as e:
            failed.append({"file": str(file_path), "error": str(e)})

    return {
        "processed_count": len(processed),
        "failed_files": failed,
        "created_notes": [p["note_path"] for p in processed]
    }


# ───────────────────────────────────────────
# CLI Entry Point
# ───────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Unified Knowledge Ingestion Bridge")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Voice
    voice_parser = subparsers.add_parser("voice", help="Ingest audio file")
    voice_parser.add_argument("--file", "-f", required=True, help="Path to audio file")
    voice_parser.add_argument("--title", "-t", help="Note title")

    # Text
    text_parser = subparsers.add_parser("text", help="Ingest text file")
    text_parser.add_argument("--file", "-f", required=True, help="Path to text file")
    text_parser.add_argument("--title", "-t", help="Note title")
    text_parser.add_argument("--tags", help="Comma-separated tags")

    # Web
    web_parser = subparsers.add_parser("web", help="Ingest web URL")
    web_parser.add_argument("--url", "-u", required=True, help="URL to extract")
    web_parser.add_argument("--title", "-t", help="Note title")

    # Batch
    batch_parser = subparsers.add_parser("batch", help="Batch process directory")
    batch_parser.add_argument("--dir", "-d", required=True, help="Directory to watch")
    batch_parser.add_argument("--no-archive", action="store_true", help="Don't move processed files")

    args = parser.parse_args()

    if args.command == "voice":
        result = ingest_voice(args.file, args.title)
        print(f"✅ Created: {result['note_path']}")
        print(f"   Words: {result['word_count']}")

    elif args.command == "text":
        tags = args.tags.split(",") if args.tags else None
        result = ingest_text(args.file, args.title, tags)
        print(f"✅ Created: {result['note_path']}")

    elif args.command == "web":
        result = ingest_web(args.url, args.title)
        print(f"✅ Created: {result['note_path']}")
        print(f"   Links found: {len(result.get('extracted_links', []))}")

    elif args.command == "batch":
        result = batch_ingest(args.dir, auto_archive=not args.no_archive)
        print(f"✅ Processed: {result['processed_count']}")
        if result["failed_files"]:
            print(f"❌ Failed: {len(result['failed_files'])}")
            for f in result["failed_files"]:
                print(f"   - {f['file']}: {f['error']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
