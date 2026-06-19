#!/usr/bin/env bash
# =============================================================================
# Reasonix Knowledge System — Cross-Device Setup
# =============================================================================
# 一键初始化：下载 Node.js → 安装 enquire-mcp → 注册 MCP Server → 创建知识库
#
# 用法:
#   chmod +x setup.sh && ./setup.sh
#
# 可选参数:
#   --vault <path>   Obsidian Vault 路径（默认 ~/Documents/Obsidian Vault）
#   --skip-node      跳过 Node.js 下载（已安装时使用）
#   --readonly       MCP Server 只读模式（不传 --enable-write）
# =============================================================================

set -euo pipefail

# ── 颜色 ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*"; }

# ── 默认配置 ──
VAULT_PATH="${HOME}/Documents/Obsidian Vault"
SKIP_NODE=false
READONLY=false
NODE_VERSION="v22.12.0"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NODE_DIR="${SCRIPT_DIR}/nodejs"

# ── 解析参数 ──
while [[ $# -gt 0 ]]; do
  case "$1" in
    --vault)    VAULT_PATH="$2"; shift 2 ;;
    --skip-node) SKIP_NODE=true; shift ;;
    --readonly)  READONLY=true; shift ;;
    *) err "未知参数: $1"; exit 1 ;;
  esac
done

echo ""
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║   Reasonix Knowledge System — Setup              ║"
echo "  ║   基于 Fable5 提示词工程的知识库系统               ║"
echo "  ╚══════════════════════════════════════════════════╝"
echo ""

# ── Step 1: 检测系统 ──
info "Step 1/5 — 检测系统环境"

ARCH=""
case "$(uname -m)" in
  x86_64) ARCH="x64" ;;
  arm64)  ARCH="arm64" ;;
  *) err "不支持的架构: $(uname -m)"; exit 1 ;;
esac
OS="$(uname -s)"
ok "系统: ${OS} / ${ARCH}"

# ── Step 2: Node.js ──
if $SKIP_NODE; then
  info "Step 2/5 — 跳过 Node.js 安装 (--skip-node)"
elif [ -x "${NODE_DIR}/bin/node" ]; then
  ok "Step 2/5 — Node.js 已存在: $(${NODE_DIR}/bin/node --version)"
else
  info "Step 2/5 — 下载 Node.js ${NODE_VERSION} (${ARCH})..."
  
  NODE_TAR="node-${NODE_VERSION}-darwin-${ARCH}.tar.gz"
  NODE_URL="https://nodejs.org/dist/${NODE_VERSION}/${NODE_TAR}"
  
  curl -fsSL "$NODE_URL" -o "/tmp/${NODE_TAR}" || {
    err "下载失败: $NODE_URL"
    exit 1
  }
  
  mkdir -p "${NODE_DIR}"
  tar -xzf "/tmp/${NODE_TAR}" -C "${NODE_DIR}" --strip-components=1
  rm -f "/tmp/${NODE_TAR}"
  
  ok "Node.js $(${NODE_DIR}/bin/node --version) 安装完成"
fi

export PATH="${NODE_DIR}/bin:${PATH}"

# ── Step 3: enquire-mcp ──
info "Step 3/5 — 安装 Obsidian MCP Server (enquire-mcp)"

if "${NODE_DIR}/bin/npx" -y @oomkapwn/enquire-mcp serve --version 2>/dev/null; then
  ok "enquire-mcp 可用"
else
  "${NODE_DIR}/bin/npm" install -g --prefix "${NODE_DIR}" @oomkapwn/enquire-mcp 2>&1 | tail -3
  ok "enquire-mcp 安装完成"
fi

# ── Step 4: Vault ──
info "Step 4/5 — 检查 Obsidian Vault"

if [ -d "${VAULT_PATH}" ]; then
  ok "Vault 已存在: ${VAULT_PATH}"
else
  warn "Vault 不存在，创建新 Vault: ${VAULT_PATH}"
  mkdir -p "${VAULT_PATH}/.obsidian"
  echo '{}' > "${VAULT_PATH}/.obsidian/app.json"
fi

# 更新 reasonix.toml 中的 Vault 路径占位符
if [ -f "${SCRIPT_DIR}/reasonix.toml" ]; then
  if grep -q '<YOUR_VAULT_PATH>' "${SCRIPT_DIR}/reasonix.toml"; then
    sed -i '' "s|<YOUR_VAULT_PATH>|${VAULT_PATH}|g" "${SCRIPT_DIR}/reasonix.toml"
    ok "已更新 reasonix.toml → ${VAULT_PATH}"
  fi
fi

# 同步知识库文件到 Vault
if [ -d "${SCRIPT_DIR}/knowledge-base" ]; then
  info "同步知识库到 Vault..."
  
  # 提示词知识库
  if [ -f "${SCRIPT_DIR}/knowledge-base/prompts/fable5/fable5-modules.md" ]; then
    mkdir -p "${VAULT_PATH}/提示词知识库"
    cp "${SCRIPT_DIR}/knowledge-base/prompts/fable5/fable5-modules.md" \
       "${VAULT_PATH}/提示词知识库/Fable5 系统提示词模块.md" 2>/dev/null || true
    cp "${SCRIPT_DIR}/knowledge-base/prompts/fable5/fable5-full-prompt.md" \
       "${VAULT_PATH}/提示词知识库/Fable5 完整提示词参考.md" 2>/dev/null || true
    cp "${SCRIPT_DIR}/knowledge-base/templates/skill-template.md" \
       "${VAULT_PATH}/提示词知识库/Skill 构造模板.md" 2>/dev/null || true
    ok "提示词知识库已同步"
  fi
  
  # 知识库索引
  if [ ! -f "${VAULT_PATH}/知识库索引.md" ]; then
    cp "${SCRIPT_DIR}/knowledge-base/skills-output/README.md" \
       "${VAULT_PATH}/Skills输出/README.md" 2>/dev/null || true
    mkdir -p "${VAULT_PATH}/专业知识库" "${VAULT_PATH}/Skills输出"
  fi
fi

# ── Step 5: MCP Server 注册 ──
info "Step 5/5 — 注册 MCP Server"

MCP_COMMAND="${NODE_DIR}/bin/npx"
MCP_ARGS="-y @oomkapwn/enquire-mcp serve --vault \"${VAULT_PATH}\""
$READONLY || MCP_ARGS="${MCP_ARGS} --enable-write"

CONFIG_FILE="${HOME}/.reasonix/config.toml"

if grep -q 'name\s*=\s*"obsidian"' "${CONFIG_FILE}" 2>/dev/null; then
  ok "MCP Server 'obsidian' 已注册"
else
  warn "请手动在 Reasonix 中注册 MCP Server:"
  echo ""
  echo "  在 Reasonix 中执行:"
  echo "  /install-source --kind mcp --name obsidian \\"
  echo "    --command \"${MCP_COMMAND}\" \\"
  echo "    --args '-y @oomkapwn/enquire-mcp serve --vault \"${VAULT_PATH}\"${READONLY:+} $($READONLY || echo ' --enable-write')' \\"
  echo "    --env '{\"PATH\":\"${NODE_DIR}/bin:/usr/bin:/bin\"}'"
  echo ""
fi

# ── 完成 ──
echo ""
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║  ✅ Setup Complete!                              ║"
echo "  ╚══════════════════════════════════════════════════╝"
echo ""
echo "  📁 Vault:    ${VAULT_PATH}"
echo "  📁 Node.js:  ${NODE_DIR}"
echo "  🛠️  MCP:      enquire-mcp ($($READONLY && echo 'readonly' || echo 'read+write'))"
echo ""
echo "  🚀 快速开始:"
echo "     /skill-generator 我需要一个 [描述] 的 Skill"
echo "     /meeting-notes-organizer [会议对话]"
echo ""
