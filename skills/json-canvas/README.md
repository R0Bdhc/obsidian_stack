# JSON Canvas Skill

Create and edit JSON Canvas (`.canvas`) files for Obsidian.

## When to Use

- Generating visual diagrams, knowledge maps, or flowcharts
- Creating project boards or kanban boards
- Building mind maps from interconnected notes
- Visualizing relationships between concepts or modules

## What It Teaches

This skill teaches the **JSON Canvas Spec 1.0**, which Obsidian uses to render visual canvases.

### Canvas File Structure

A `.canvas` file is JSON containing:

```json
{
  "nodes": [
    {
      "id": "node1",
      "type": "text",
      "x": -200,
      "y": -100,
      "width": 250,
      "height": 60,
      "text": "Main Concept"
    },
    {
      "id": "node2",
      "type": "file",
      "x": 200,
      "y": -100,
      "width": 250,
      "height": 60,
      "file": "Knowledge/Concepts/Sub-Topic.md"
    }
  ],
  "edges": [
    {
      "id": "edge1",
      "fromNode": "node1",
      "toNode": "node2",
      "fromSide": "right",
      "toSide": "left"
    }
  ]
}
```

### Node Types

| Type | Description | Use For |
|------|-------------|---------|
| `text` | Plain text node | Labels, concepts, short notes |
| `file` | Link to vault file | Connecting to existing notes |
| `link` | External URL | References to web resources |
| `group` | Container for other nodes | Grouping related nodes |

### Layout Best Practices

- **Center the main concept** at `(0, 0)`
- **Place related nodes** in a radial or hierarchical pattern
- **Use consistent spacing**: 200-400px between nodes
- **Label edges** when the relationship isn't obvious
- **Group related nodes** using `group` type with background color

## Workflow: Creating a Knowledge Map

1. **Identify central concept** — place at `(0, 0)`
2. **Add related notes** as `file` nodes positioned around the center
3. **Add relationship labels** using `text` nodes near edges
4. **Connect nodes** with `edges` specifying `fromSide` and `toSide`
5. **Group by theme** using `group` nodes with colors
6. **Save** as `.canvas` in the `Canvas/` folder

## Example: Project Architecture Map

```json
{
  "nodes": [
    {"id": "main", "type": "text", "x": 0, "y": 0, "width": 200, "height": 60, "text": "main.py"},
    {"id": "parser", "type": "text", "x": -300, "y": -150, "width": 200, "height": 60, "text": "log_parser.py"},
    {"id": "llm", "type": "text", "x": 300, "y": -150, "width": 200, "height": 60, "text": "llm_analyzer.py"},
    {"id": "report", "type": "text", "x": 0, "y": 200, "width": 200, "height": 60, "text": "report_generator.py"}
  ],
  "edges": [
    {"id": "e1", "fromNode": "main", "toNode": "parser", "fromSide": "left", "toSide": "right"},
    {"id": "e2", "fromNode": "main", "toNode": "llm", "fromSide": "right", "toSide": "left"},
    {"id": "e3", "fromNode": "main", "toNode": "report", "fromSide": "bottom", "toSide": "top"}
  ]
}
```

## Reference

- **Spec**: [jsoncanvas.org/spec/1.0/](https://jsoncanvas.org/spec/1.0/)
