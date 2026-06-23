---
name: check-ansys-env
description: 检查 CAE Agent 完整环境状态，包括 LLM 连通性、PyMAPDL 可用性和 PyMechanical 版本检测。
---

# 环境检查技能

汇总三个子系统状态，提供一站式环境诊断面板。

## 执行流程

并行调用三个 MCP 工具（来自 `ansys-local` MCP 服务器）：

1. `health_check` — LLM 连通性 + DeepSeek API 状态
2. `mapdl_status` — PyMAPDL 可导入性 + MAPDL.exe 定位 + 工作目录
3. `mechanical_status` — PyMechanical 可导入性 + 版本检测 + 242+ 支持

三个工具独立无依赖，可以并行调用。

## 输出格式

```
## CAE Agent 环境状态

### LLM 分析层
- Provider: deepseek / none
- Model: deepseek-v4-pro
- 已配置: ✅/❌
- 可连通: ✅/❌ (检查时间: ...)
- 模式: LLM增强 / 本地规则回退

### PyMAPDL 执行层
- 可导入: ✅/❌ (错误: ...)
- MAPDL.exe: <路径> / 未找到
- ANSYS241_DIR: <路径> (存在: ✅/❌)
- 支持格式: .inp .dat .mac
- 运行时目录: runtime_data/

### PyMechanical 层 (242+)
- 可导入: ✅/❌
- Mechanical.exe: <路径> / 未找到
- 检测版本: 242 / 251 / ... / 未检测到
- 版本支持: ✅/❌
```

## 用例

- 新环境首次配置验证
- 许可证或路径变更后排查
- 用户问 "ANSYS 能不能用" / "环境对不对"
