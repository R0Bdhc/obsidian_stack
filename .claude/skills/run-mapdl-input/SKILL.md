---
name: run-mapdl-input
description: 执行 MAPDL 输入文件（.inp/.dat/.mac）并可选自动分析结果日志。
---

# MAPDL 输入文件执行技能

启动 ANSYS MAPDL 求解器，执行用户的输入文件，收集日志并可选串联分析。

## 输入

用户会提供：
- `.inp` / `.dat` / `.mac` 文件的绝对路径
- 是否执行后自动分析（默认 true）

## 执行流程

所有操作通过 `ansys-local` MCP 服务器的工具完成，无需启动 FastAPI 服务。

### Step 1: 确认文件

用 Read 工具确认输入文件存在且内容合理（非空、包含 `/PREP7` 或 `/SOLU` 等 APDL 关键字）。

### Step 2: 检查环境

调用 MCP 工具 `mapdl_status` 确认：
- `pymapdl_importable` 为 true
- `detected_mapdl_exec` 不为 null

如果环境不满足，告知用户具体问题并终止，给出修复建议。

### Step 3: 执行

调用 MCP 工具 `mapdl_execute`：
```
mapdl_execute(
    input_file_path="<绝对路径>",
    working_directory="D:\\ansysagent\\ansys_workspace"
)
```

### Step 4: 自动分析（可选，默认开启）

如果用户需要自动分析（默认），调用 MCP 工具 `log_analyze`：
```
log_analyze(log_path="<primary_log_path>")
```
其中 `primary_log_path` 来自 `mapdl_execute` 的返回结果。

### Step 5: 呈现结果

从返回中提取关键字段汇总给用户。

## 输出格式

```
## MAPDL 执行结果

**输入文件**: <路径>
**状态**: ✅ 执行成功 / ❌ 执行失败
**主日志**: <primary_log_path>

### 求解结果数据
| 指标 | 最大值 |
|------|--------|
| 合位移 (USUM) | ... |
| Von Mises (SEQV) | ... |

### 求解器输出预览
```
<mapdl_output_preview>
```

### 自动分析（如果有）
- 错误数: N
- 分析模式: ...
- 报告: reports/...
```

## 约束

- 不支持 `.wbpj`（Workbench 工程文件），如用户传入请提示先导出为 `.inp`
- 真实启动需要 ANSYS 许可证可用
- 执行可能耗时数分钟，需提醒用户等待
