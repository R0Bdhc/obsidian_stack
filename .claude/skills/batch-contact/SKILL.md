---
name: batch-contact
description: 基于 Named Selection 前缀批量创建 Mechanical 接触对（242+）。默认预览模式。
---

# 批量接触自动化技能

按 Named Selection 前缀配对规则，在 ANSYS Mechanical 中批量创建接触区域。

## 配对规则

```
NS_SRC_BOLT_01  +  NS_TGT_BOLT_01  →  AUTO_CONTACT_BOLT_01
NS_SRC_FLANGE   +  NS_TGT_FLANGE   →  AUTO_CONTACT_FLANGE

规则: source 前缀和 target 前缀去除后，同名后缀的视为一对
```

## 输入

用户需提供以下参数（缺失时交互询问）：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| source_prefix | 源面 Named Selection 前缀 | 必填 |
| target_prefix | 目标面 Named Selection 前缀 | 必填 |
| contact_type | 接触类型 | Frictionless |
| contact_name_prefix | 生成接触的名称前缀 | AUTO_CONTACT_ |
| launch | 是否真实启动 Mechanical | false |

支持的 contact_type: Bonded, Frictional, Frictionless, NoSeparation, Rough

## 执行流程

使用 `ansys-local` MCP 服务器的 `mechanical_batch_contact` 工具。

### 预览模式（默认，launch=false）

```
mechanical_batch_contact(
    source_prefix="<用户输入>",
    target_prefix="<用户输入>",
    contact_type="<用户输入>",
    contact_name_prefix="<用户输入>",
    launch=false
)
```

返回生成的 Mechanical 脚本预览和配对策略。

### 执行模式（launch=true）

先调用 `mechanical_status` 确认环境（版本 ≥ 242），再调用：

```
mechanical_batch_contact(
    source_prefix="<用户输入>",
    target_prefix="<用户输入>",
    contact_type="<用户输入>",
    contact_name_prefix="<用户输入>",
    launch=true
)
```

## 输出格式

### 预览模式
```
## 批量接触方案预览

- 策略: Named Selection 前缀配对
- 接触类型: Frictionless
- 前缀: NS_SRC_ ↔ NS_TGT_

### 生成的 Mechanical 脚本
```python
<脚本内容>
```
```

### 执行模式
```
## 批量接触执行结果

- 版本: 242
- 配对数: N
- 已创建接触: AUTO_CONTACT_BOLT_01, AUTO_CONTACT_FLANGE, ...
- 缺失源面后缀: [...]
- 缺失目标面后缀: [...]
```

## 注意事项

- 仅在 242+ 版本可用，241 环境仅支持预览
- 需要 .mechdb 工程中已有对应的 Named Selections
- 当前不具备按几何特征自动创建 Named Selection 的能力（预留功能）
