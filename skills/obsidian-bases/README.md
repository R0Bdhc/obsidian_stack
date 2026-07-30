# Obsidian Bases Skill

Create and edit Obsidian Bases (`.base`) files — database views for structured data management.

## When to Use

- Creating database views for projects, tasks, or contacts
- Building dashboards to track progress or metrics
- Managing structured data with filters, formulas, and sorting
- Needing a spreadsheet-like interface over Markdown notes

## What It Teaches

This skill teaches the **Obsidian Bases** format, which provides database functionality within Obsidian.

### Base File Structure

A `.base` file defines:

```yaml
---
name: "Project Tracker"
fields:
  - name: "Project"
    type: "title"
  - name: "Status"
    type: "select"
    options: ["Active", "On Hold", "Completed", "Archived"]
  - name: "Priority"
    type: "select"
    options: ["P0", "P1", "P2", "P3"]
  - name: "Due Date"
    type: "date"
  - name: "Progress"
    type: "number"
    format: "percent"
  - name: "Tags"
    type: "tags"
views:
  - name: "All Projects"
    type: "table"
  - name: "Active Only"
    type: "table"
    filter: "Status = Active"
  - name: "By Priority"
    type: "kanban"
    groupBy: "Priority"
---
```

### Field Types

| Type | Use For | Example |
|------|---------|---------|
| `title` | Primary identifier | Project name |
| `text` | Short text | Description |
| `number` | Numeric values | Progress %, count |
| `date` | Dates | Due date, created |
| `select` | Single choice | Status, priority |
| `multi_select` | Multiple choices | Tags, categories |
| `tags` | Obsidian tags | `#project #active` |
| `checkbox` | Boolean | Completed |
| `formula` | Computed values | `= Progress * 100` |
| `relation` | Link to other base | Related project |
| `rollup` | Aggregate relation | Sum of subtasks |

### View Types

| View | Best For |
|------|----------|
| `table` | Spreadsheet-like editing, sorting, filtering |
| `gallery` | Visual cards with images/previews |
| `kanban` | Status workflows, drag-and-drop |
| `calendar` | Date-based planning |
| `list` | Simple compact display |

## Workflow: Creating a Project Tracker

1. **Define fields** — identify what data to track (status, priority, dates)
2. **Create base** — save as `.base` file in `Bases/` folder
3. **Add views** — create filtered views for different contexts
4. **Link notes** — use `relation` fields to connect to project notes
5. **Add formulas** — compute derived values (e.g., days until due)
6. **Use in daily workflow** — open base view to check project status

## Example: Project Tracker Base

```yaml
---
name: "项目追踪"
fields:
  - name: "项目名称"
    type: "title"
  - name: "状态"
    type: "select"
    options: ["进行中", "暂停", "已完成", "已归档"]
  - name: "优先级"
    type: "select"
    options: ["P0", "P1", "P2"]
  - name: "负责人"
    type: "text"
  - name: "开始日期"
    type: "date"
  - name: "截止日期"
    type: "date"
  - name: "进度"
    type: "number"
    format: "percent"
  - name: "相关笔记"
    type: "relation"
    target: "Projects"
views:
  - name: "所有项目"
    type: "table"
  - name: "进行中"
    type: "table"
    filter: "状态 = 进行中"
    sort: "优先级 asc"
  - name: "优先级看板"
    type: "kanban"
    groupBy: "优先级"
---
```
