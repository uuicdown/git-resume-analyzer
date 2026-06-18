# Git Resume Analyzer

> 从 git 提交历史生成专业简历内容。
>
> **AI 直接进仓库看 diff、读源码、写简历。脚本只是可选辅助。**

AI（你正在对话的助手）会直接在你的项目目录中工作——跑 git log、看 diff、读源码。你只需要告诉它作者名字，它就能自己完成全部分析。

脚本是可选的辅助工具，用来快速获取统计概览。但真正的深度分析来自 AI 直接阅读代码变更。

---

## 快速开始

```bash
# 方式 A：让 AI 直接操作（推荐）
# 在项目目录中直接对 AI 说：
# "帮我分析 git 产出，作者名是 xxx"

# 方式 B：用脚本先看一下统计
python git_resume_analyzer.py --author "你的名字" --json --no-merges
```

### 参数说明

| 参数 | 作用 |
|------|------|
| `--author` | **必需**。Git 作者名称 |
| `--since YYYY-MM-DD` | 开始日期 |
| `--until YYYY-MM-DD` | 结束日期 |
| `--no-merges` | 过滤 Merge commit（建议开启） |
| `--json` | 输出 JSON（给 AI 用） |
| `--output file.json` | 输出到文件 |
| `--top-n 10` | 限制输出 commit 数量 |

---

## 文件说明

| 文件 | 用途 |
|------|------|
| **GIT-RESUME-SKILL.md** | AI 规则手册——告诉 AI 怎么分析 git 数据写简历 |
| **git_resume_analyzer.py** | 数据采集脚本（纯采集，零判断） |
| **examples/** | 输出示例参考 |

---

## 完整流程

```bash
# 方式 A：AI 全权处理（推荐）
# 在项目目录中，直接对 AI 说：
# "帮我分析 git 产出，作者名是 luoxiaogen"
# AI 会自动跑 git log、看 diff、读源码、生成简历

# 方式 B：先用脚本看统计，再让 AI 深度分析
python git_resume_analyzer.py --author "luoxiaogen" --json --no-merges
# 然后把输出给 AI，说：
# "这是我 git 产出的统计数据，请帮我看关键 diff 并生成简历"
```

---

## 部署到各 AI 平台

### 编码助手类（项目级配置）

| 平台 | 部署方式 |
|------|---------|
| **Claude Code** | `CLAUDE.md` |
| **Cursor** | `.cursorrules` |
| **Windsurf** | `.windsurfrules` |
| **Cline / Roo Code** | `CLAUDE.md` |
| **GitHub Copilot** | `.github/copilot-instructions.md` |
| **Amazon Q Developer** | `.amazon-q/instructions.md` |
| **CodeGeeX** | `.codegeex/instructions.md` |
| **OpenClaw** 🦞 | `skills/<name>/SKILL.md` |
| **OpenCode** | `opencode.jsonc` + `skills/` |
| **ChatGPT (Codex / GPT-4)** | 对话或 Projects Instructions |

```bash
# 一键部署（选一个即可）
cp GIT-RESUME-SKILL.md CLAUDE.md                          # Claude Code / Cline
cp GIT-RESUME-SKILL.md .cursorrules                       # Cursor
cp GIT-RESUME-SKILL.md .windsurfrules                     # Windsurf
cp GIT-RESUME-SKILL.md .github/copilot-instructions.md    # GitHub Copilot
mkdir -p ~/.config/openclaw/skills/git-resume-analyzer     # OpenClaw 🦞
cp GIT-RESUME-SKILL.md ~/.config/openclaw/skills/git-resume-analyzer/SKILL.md
```

### 对话类（手动注入）

| 平台 | 方式 |
|------|------|
| **Claude.ai Projects** | Project Knowledge 上传文件 |
| **ChatGPT Custom GPT** | Instructions 粘贴 / Knowledge 上传 |
| **Gemini Gems** | Instructions 粘贴 |
| **DeepSeek Chat** | 对话中粘贴 |

---

## 依赖

- **Git**（AI 直接操作项目目录时需要）
- **Python 3.7+**（仅在使用脚本时需要，非必需）
