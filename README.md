# Git Resume Analyzer

![Skill](https://img.shields.io/badge/-AI%20Skill-8A2BE2)
![Platforms](https://img.shields.io/badge/platforms-10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> 从 git 提交历史生成求职材料：简历、面试讲稿、技术文章。
>
> AI 直接进仓库看 diff、读源码、写材料；脚本只做数据采集。

## 这是什么

一个给 AI 助手用的 skill：把一个人的 git 提交历史，变成能写进简历或讲稿的内容。

它分两段，各管各的：

- **`git_resume_analyzer.py`** —— 只做数据采集。跑 `git log`，把每个提交的哈希、时间、标题、正文、文件列表和增删行数导出成结构化 JSON 或文本摘要。
- **`GIT-RESUME-SKILL.md`** —— 规则手册。告诉 AI 怎么基于这些数据、再去读真正的 diff 和源码，推断每个提交"解决了什么问题、用了什么技术、怎么实现的"，最后按模板写成简历/讲稿。

采集和判断分开：脚本不猜语义，语义全由 AI 从代码里读出来。

## 快速开始

```bash
# 方式 A（推荐）：让 AI 直接操作
# 在项目目录里对 AI 说：
#   "帮我分析 git 产出，作者名是 xxx"

# 方式 B：先用脚本看统计
python git_resume_analyzer.py --author "你的名字" --json --no-merges
```

### 参数

| 参数 | 作用 |
|------|------|
| `--author` | **必需**。Git 作者名称；可多次传入，合并同一人的多个身份 |
| `--since YYYY-MM-DD` | 开始日期 |
| `--until YYYY-MM-DD` | 结束日期 |
| `--no-merges` | 过滤 Merge commit（建议开启） |
| `--json` | 输出 JSON（给 AI 用） |
| `--output file.json` | 输出到文件 |
| `--top-n 10` | 限制输出的 commit 数量 |

示例：合并两个作者身份

```bash
python git_resume_analyzer.py --author "your-name" --author "your-alias" --json --no-merges
```

## 文件说明

| 文件 | 用途 |
|------|------|
| **GIT-RESUME-SKILL.md** | 主入口 —— AI 规则手册，指导怎么分析 git 数据写成简历 |
| **skills/git-resume-analyzer/SKILL.md** | OpenClaw 兼容路径，内容同上 |
| **git_resume_analyzer.py** | 数据采集脚本（纯采集，不做语义判断） |
| **test_git_resume.py** | 回归测试（标准库 unittest） |
| **examples/sample-output.md** | 脚本输出的 JSON 示例 |
| **examples/self-analysis.md** | 本 skill 分析自己仓库的完整样例 |

## 部署到各 AI 平台

### 编码助手类

| 平台 | 部署方式 |
|------|---------|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` |
| Windsurf | `.windsurfrules` |
| Cline / Roo Code | `CLAUDE.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Amazon Q Developer | `.amazon-q/instructions.md` |
| CodeGeeX | `.codegeex/instructions.md` |
| OpenClaw | `skills/<name>/SKILL.md` |
| OpenCode | `opencode.jsonc` + `skills/` |

```bash
# 选一个即可
cp GIT-RESUME-SKILL.md CLAUDE.md
cp GIT-RESUME-SKILL.md .cursorrules
cp GIT-RESUME-SKILL.md .windsurfrules
cp GIT-RESUME-SKILL.md .github/copilot-instructions.md
```

### 对话类

| 平台 | 方式 |
|------|------|
| Claude Projects / ChatGPT Custom GPT | 上传或粘贴规则手册 |
| Gemini Gems | Instructions 粘贴 |
| DeepSeek Chat | 对话中粘贴 |

## 跑测试

```bash
python test_git_resume.py
```

会在系统临时目录建一个一次性 git 仓库，覆盖三个解析场景（正文含 `|`/多行、双父的合并提交）并断言输出，跑完自动清理。

## 依赖

- **Git**（脚本和 AI 直接操作项目都需要）
- **Python 3.7+**（仅使用脚本时需要，非必需）

## 许可

MIT
