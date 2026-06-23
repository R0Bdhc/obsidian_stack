# cae-agent

一个面向 ANSYS 场景的最小可运行 CAE 智能辅助项目骨架。

当前版本的核心链路：

1. 读取 `.out` / `.log` 日志
2. 检测常见求解错误
3. 调用 DeepSeek LLM 生成原因分析与修改建议
4. 自动输出 Markdown 报告
5. 通过 FastAPI 暴露简单接口
6. 封装 PyMAPDL 执行 `.inp/.dat/.mac`
7. 预留 PyMechanical 242+ 批量接触自动化

这个版本刻意保持简单，重点是：

- 能运行
- 易理解
- 易扩展
- 适合边做边学

## 1. 当前目录结构

```text
cae-agent/
├─ main.py
├─ ansys_runner.py
├─ mechanical_runner.py
├─ log_parser.py
├─ llm_analyzer.py
├─ report_generator.py
├─ requirements.txt
├─ .env.example
├─ README.md
├─ sample_inputs/
│  └─ bar_example.inp
├─ sample_logs/
│  └─ demo_solver.out
├─ ansys_workspace/
├─ runtime_data/
├─ mechanical_workspace/
└─ reports/
```

## 2. 每个文件的职责

### `main.py`

FastAPI 入口文件。

负责：

- 启动 Web 服务
- 接收日志路径或日志文本
- 串联日志解析、LLM 分析、报告生成
- 提供健康检查接口（含 LLM 连通性缓存）
- 暴露 MAPDL 执行和 Mechanical 批量接触接口

### `log_parser.py`

日志解析模块。

负责：

- 读取日志文件（UTF-8，忽略解码错误）
- 按正则模式检测常见错误关键词
- 截取错误附近的日志片段，返回标准化错误结果

### `ansys_runner.py`

ANSYS / PyMAPDL 接口模块。

负责：

- 检查 PyMAPDL 是否可导入
- 读取 ANSYS241_DIR / ANSYSLIC_DIR / AWP_ROOT241 环境变量
- 自动搜索 MAPDL.exe 可执行文件
- 返回最小 APDL 示例命令（两节点 LINK180 拉杆静力分析）
- 重定向 PyMAPDL 运行期用户目录到 runtime_data，避免系统权限问题
- 在 launch_mapdl=True 时真实启动 MAPDL 并执行
- 执行真实的 .inp/.dat/.mac 输入文件
- 自动收集工作目录中的 .out/.log/.err 日志
- 选择最合适的主日志文件用于后续分析

### `mechanical_runner.py`

242+ PyMechanical 能力层。

负责：

- 检测 PyMechanical 是否可导入
- 按版本号搜索 Mechanical 可执行文件（支持 242/251/252/261/271/272）
- 重定向 PyMechanical 运行期用户目录到 runtime_data
- 返回 242+ 能力方案说明
- 基于 Named Selection 前缀批量配对接触（如 NS_SRC_xxx + NS_TGT_xxx）
- 生成并预览 Mechanical 执行脚本
- 在 242+ 环境中可真实启动 Mechanical 执行批量接触创建

### `llm_analyzer.py`

LLM 分析模块。

负责：

- 根据检测到的错误构造专业 CAE 分析提示词
- 调用 DeepSeek Chat API（兼容 OpenAI SDK）
- 支持 DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL / DEEPSEEK_MODEL 灵活配置
- LLM 调用成功后自动更新健康检查缓存
- 在无 API Key 或调用失败时，提供本地规则回退分析（奇异矩阵、不收敛、接触穿透三类）
- 去重并保持分析结果的原始顺序

### `report_generator.py`

报告生成模块。

负责：

- 把日志检测结果和 LLM 分析结果拼成 Markdown
- 按时间戳命名，保存到 `reports/` 目录

## 3. 环境要求

- Python 3.11+
- 已安装 ANSYS 的机器更适合后续扩展 PyMAPDL 能力
- （可选）已安装 ANSYS 242+ 以启用 PyMechanical 批量接触自动化

## 4. 安装依赖

```bash
pip install -r requirements.txt
```

核心依赖：

```
fastapi==0.115.12
uvicorn[standard]==0.34.2
openai==1.79.0
ansys-mapdl-core==0.71.0
python-dotenv==1.1.0
```

> `openai` SDK 用于调用 DeepSeek API，DeepSeek 兼容 OpenAI 接口协议，通过 `base_url` 切换。

如果你未来要启用 242+ PyMechanical 能力，建议额外安装：

```bash
pip install ansys-mechanical-core
```

## 5. 配置 LLM API Key

项目根目录的 `.env` 文件（从 `.env.example` 复制）：

```env
DEEPSEEK_API_KEY=sk-xxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
ANSYS241_DIR=D:\ANSYS Inc\v241\ANSYS
ANSYSLIC_DIR=D:\ANSYS Inc\Shared Files\Licensing
AWP_ROOT241=D:\ANSYS Inc\v241
```

> 如果 DEEPSEEK_API_KEY 留空，系统也能运行，只是 LLM 分析会回退到本地规则模式。

## 6. 启动服务

```bash
uvicorn main:app --reload
```

启动后访问：

- `http://127.0.0.1:8000/docs` — Swagger 接口文档
- `http://127.0.0.1:8000/health` — LLM 连通性检查
- `http://127.0.0.1:8000/mapdl-status` — PyMAPDL 环境状态
- `http://127.0.0.1:8000/ansys-demo` — APDL 示例预览
- `http://127.0.0.1:8000/mechanical-status` — PyMechanical 环境状态

## 7. 测试方式

### 方法 A：直接分析示例日志文件

请求地址：

`POST /analyze-log`

请求体示例：

```json
{
  "log_path": "D:\\ansysagent\\sample_logs\\demo_solver.out"
}
```

### 方法 B：直接传日志文本

```json
{
  "log_text": "*** ERROR ***\nconvergence failed at substep 12\ncontact penetration detected"
}
```

### 方法 C：查看 ANSYS 接口示例

请求地址：

`GET /ansys-demo`

这个接口不会真实启动 ANSYS，只会返回：

- 最小 APDL 命令列表
- 示例分析类型
- 检测到的 MAPDL.exe 路径
- 下一步如何真实执行

### 方法 D：执行最小 ANSYS 示例

请求地址：

`POST /run-ansys-demo`

请求体示例 1：仅预览，不真实启动

```json
{
  "launch_mapdl": false
}
```

请求体示例 2：尝试真实启动 MAPDL

```json
{
  "launch_mapdl": true,
  "working_directory": "D:\\ansysagent\\ansys_workspace"
}
```

说明：

- `launch_mapdl=false` 时，项目一定能返回示例结果
- `launch_mapdl=true` 时，需要你的机器已经正确安装并可启动 ANSYS / MAPDL

### 方法 E：执行真实 MAPDL 输入文件

请求地址：

`POST /run-mapdl-input`

请求体示例：

```json
{
  "input_file_path": "D:\\ansysagent\\sample_inputs\\bar_example.inp",
  "working_directory": "D:\\ansysagent\\ansys_workspace",
  "analyze_after_run": true
}
```

这个接口会做 4 件事：

1. 启动 MAPDL
2. 执行你传入的 `.inp/.dat/.mac`
3. 自动收集工作目录中的 `.out/.log/.err`
4. 可选地继续调用日志分析与 Markdown 报告链路

当前推荐接入的真实工程文件类型：

- `.inp`
- `.dat`
- `.mac`

当前不直接支持：

- `.wbpj`

原因是 `.wbpj` 属于 Workbench 工程项目文件，不是 PyMAPDL 直接执行的输入文件。
如果你的模型来自 Workbench，建议先导出 MAPDL 输入文件，再接入当前接口。

### 方法 F：查看 242+ PyMechanical 能力状态

请求地址：

`GET /mechanical-status`

这个接口会返回：

- 当前是否能导入 PyMechanical
- 是否找到 242+ Mechanical 可执行文件
- 检测到的版本号以及是否在支持范围内

### 方法 G：查看 242+ PyMechanical 方案说明

请求地址：

`GET /mechanical-capabilities`

这个接口会返回：

- 推荐实现路线（Named Selection 前缀配对）
- 当前稳定能力（扫描 Named Selections、批量配对接触）
- 预留能力（按面类型创建特征型 Named Selections）

### 方法 H：预览批量接触方案

请求地址：

`POST /mechanical-contact-batch-plan`

请求体示例：

```json
{
  "source_named_selection_prefix": "NS_SRC_",
  "target_named_selection_prefix": "NS_TGT_",
  "contact_type": "Frictionless",
  "contact_name_prefix": "AUTO_CONTACT_"
}
```

这个接口会返回：

- 推荐的批量配对策略
- 生成的 Mechanical 脚本预览

配对规则：把 source 前缀和 target 前缀后面的同名后缀视为同一特征对。
例如 `NS_SRC_BOLT_01` + `NS_TGT_BOLT_01` -> `AUTO_CONTACT_BOLT_01`

### 方法 I：执行批量接触

请求地址：

`POST /mechanical-contact-batch-execute`

请求体示例：

```json
{
  "source_named_selection_prefix": "NS_SRC_",
  "target_named_selection_prefix": "NS_TGT_",
  "contact_type": "Frictionless",
  "contact_name_prefix": "AUTO_CONTACT_",
  "launch_mechanical": false,
  "working_directory": "D:\\ansysagent\\mechanical_workspace"
}
```

说明：

- `launch_mechanical=false` 时，与 /mechanical-contact-batch-plan 行为一致
- `launch_mechanical=true` 时，需要 242+ 版本的 Mechanical 环境
- 在 241 环境下默认建议只做预览

## 8. ANSYS 路径配置说明

当前版本通过环境变量或 `.env` 文件管理 ANSYS 路径：

```env
ANSYS241_DIR=D:\ANSYS Inc\v241\ANSYS
ANSYSLIC_DIR=D:\ANSYS Inc\Shared Files\Licensing
AWP_ROOT241=D:\ANSYS Inc\v241
```

它们在当前项目中的作用分别是：

- `ANSYS241_DIR`
  用于优先定位 `MAPDL.exe`，这是最有价值的一个路径。
- `AWP_ROOT241`
  作为安装根目录的备用定位路径，当 `ANSYS241_DIR` 不稳定时仍可继续推导可执行文件位置。
- `ANSYSLIC_DIR`
  用于补充运行环境信息，但它通常不是许可证服务器地址本身，所以不是 `launch_mapdl()` 的核心参数。

当前代码会优先尝试寻找这些文件：

- `D:\ANSYS Inc\v241\ANSYS\bin\winx64\MAPDL.exe`
- `D:\ANSYS Inc\v241\ANSYS\bin\winx64\MAPDL241.exe`
- `D:\ANSYS Inc\v241\ANSYS\bin\winx64\ANSYS241.exe`

另外，当前项目还会把 PyMAPDL 的运行期用户目录重定向到项目内：

`D:\ansysagent\runtime_data\localappdata`

这样做是为了避免某些环境下 `C:\Users\...\AppData\Local` 没有写权限，导致 PyMAPDL 在导入阶段就失败。

## 9. 错误检测关键词

当前在 `log_parser.py` 中维护的最小错误模式表：

| 错误代码 | 匹配模式 | 中文含义 |
|----------|----------|----------|
| `singular_matrix` | `singular matrix` | 刚度矩阵奇异 |
| `convergence_failed` | `convergence failed` | 非线性迭代不收敛 |
| `contact_penetration` | `contact penetration` | 接触穿透 |
| `license_error` | `license manager error` 等 | 许可证错误 |

可通过扩展 `ERROR_PATTERNS` 字典持续增加新的错误模式。

## 10. 返回结果说明

接口会返回：

- 是否检测到错误
- 错误列表（含错误代码、标题、描述、日志片段）
- LLM 分析结果（含分析模式、模型名、原始分析文本）
- Markdown 报告内容
- Markdown 报告保存路径

## 11. PyMAPDL 说明

当前版本已经把 PyMAPDL 纳入依赖，并在接口中提供基础环境检查。

为了保证新手开箱即跑，本版本采用"两段式"设计：

1. 默认只返回 ANSYS 调用示例
2. 只有在你明确传入 `launch_mapdl=true` 时，才尝试真实启动 MAPDL

当前内置的真实示例是：

1. 建立一个两节点 `LINK180` 拉杆
2. 施加一端固定、另一端轴向力
3. 求解静力问题
4. 读取 2 号节点的 X 向位移

## 12. 推荐的技术栈

当前阶段使用：

- `FastAPI`：接口层
- `DeepSeek API`（兼容 OpenAI SDK）：错误分析与建议生成
- `PyMAPDL`：ANSYS MAPDL 自动化
- `PyMechanical`（可选的 242+）：Mechanical 批量接触自动化
- `Markdown`：报告输出
- `python-dotenv`：环境变量管理

## 13. 后续建议的渐进式开发顺序

当前版本已完成：

1. 日志读取
2. 错误检测（4 种关键词）
3. DeepSeek LLM 分析 + 本地规则回退
4. Markdown 报告保存
5. PyMAPDL 环境检测与 MAPDL.exe 定位
6. 真实 MAPDL 执行（demo + .inp 文件）
7. 执行后自动串联日志分析链路
8. LLM 健康检查缓存（5 分钟）
9. PyMechanical 242+ 接口预留

下一步建议：

1. 扩展错误检测关键词库
2. 接入更多 MAPDL 求解类型（模态、热分析等）
3. 按面几何特征（圆柱面、平面）自动创建 Named Selections
4. 部署到 242+ 环境启用 Mechanical 批量接触执行

## 14. 参考

- DeepSeek API 文档：[https://platform.deepseek.com/api-docs](https://platform.deepseek.com/api-docs)
- PyMAPDL 文档：[https://mapdl.docs.pyansys.com/](https://mapdl.docs.pyansys.com/)
- PyMechanical 文档：[https://mechanical.docs.pyansys.com/](https://mechanical.docs.pyansys.com/)
