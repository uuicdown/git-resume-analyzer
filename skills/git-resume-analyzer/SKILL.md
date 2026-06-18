---
name: git-resume-analyzer
description: 从 git 提交历史生成专业简历内容。AI 直接进仓库看提交、读 diff、分析源码，自主完成全部语义分析——问题推断、技术栈识别、方案提取、简历撰写。脚本仅作可选辅助。
---

# Git Resume Analyzer

## 工作方式

```
你（AI）直接在 git 仓库中工作
  │
  ├─ git log            ← 看提交历史
  ├─ git show / git diff ← 看每次改了什么代码
  ├─ 读项目源码          ← 理解架构和模块
  └─ git log --numstat  ← 看代码量统计
  │
  ▼
  综合分析：问题 → 方案 → 技术 → 成果
  │
  ▼
  简历/讲稿/文章
```

**你是分析者，不是接收者**。不要等脚本喂数据——直接进项目目录，跑 git 命令、读 diff、看源码。脚本只是可选的辅助工具，不是必需环节。

---

## 第一步：自己去项目里看

### 方式 A：直接跑 git 命令（推荐，你能获得最多信息）

```bash
# 1. 看看作者做了哪些提交
git log --author="作者名" --all --oneline

# 2. 看每个提交具体改了啥（这是关键！）
git show <hash> --stat      # 改了哪些文件
git show <hash>             # 完整的 diff，看代码前后变化
git diff <hash>~1 <hash>    # 和前一个版本的差异

# 3. 统计代码量
git log --author="作者名" --all --numstat

# 4. 按时间范围筛选
git log --author="作者名" --since="2026-04-01" --until="2026-06-30"
```

**看 diff 是理解问题的核心**。不要只看 commit message——message 可能很简短。实际改了哪些代码、删了什么、加了什么判断，这些信息只在 diff 里。

### 方式 B：用 Python 脚本辅助（快速获取统计概览）

```bash
python git_resume_analyzer.py --author "作者名" --json --no-merges
```

脚本帮你快速汇总：总提交数、代码行数、时间范围。但它**不包含 diff 内容**，所以你仍然需要去看关键提交的具体 diff。

---

### 建议的工作流程

```
1. git log --oneline         → 先看有哪些提交，圈出重要/大型的
2. git show <重要提交的 hash>  → 看这些提交的完整 diff
3. 读相关源码文件             → 理解改动的模块和架构上下文
4. git log --numstat         → 统计代码量
5. 综合以上所有信息           → 撰写简历
```

---

## 脚本输出示例（JSON，快速参考用）

```json
{
  "summary": {
    "author": "luoxiaogen",
    "total_commits": 12,
    "merge_commits": 0,
    "total_lines_added": 1375,
    "total_lines_deleted": 357,
    "total_files_changed": 8,
    "date_range": "2026-04-07 ~ 2026-05-25"
  },
  "commits": [
    {
      "hash": "58c58df",
      "date": "2026-05-25",
      "title": "fix(assets): 浪潮云主机OS字段解析全面修复",
      "body": "1. 新增 parseOsInfo() 方法...\n2. 支持 V 前缀格式...\n3. 支持无 V 前缀格式...",
      "files": [
        "assets/src/main/java/.../AMachineServiceImpl.java",
        "common/src/main/java/.../Constant.java"
      ],
      "lines_added": 79,
      "lines_deleted": 7,
      "is_merge": false
    }
  ]
}
```

---

## 第二步：AI 分析规则（全部由你完成）

**关键原则**：先看 diff，再看 message。commit message 可能只有一句话，但 diff 里包含了完整的上下文——删了什么代码、加了什么判断、重构了什么逻辑。这些才是简历的素材。

以下是你需要做的全部工作：

### 规则 1：去噪与合并

**不要逐条罗列 commit**，简历不是 git log。

```
需要过滤的提交：
  - is_merge: true 的提交 → 跳过（不包含实际工作）

需要合并的提交：
  - 标题相似、时间接近、涉及相同文件 → 合并为一个项目成就
    例如：
      "fix: OS字段解析全面修复" (+79行)
      "fix: OS字段解析及CPU非空约束修复" (+54行)
      → 合并为「设计多格式 OS 字段解析引擎，累计 +133 行」

  - 同一功能的多次迭代（feat → fix → refactor）→ 合并为一个完整故事
```

### 规则 2：模块分类（从文件路径推断）

用户没有配置模块映射，你需要从**文件路径字符串**自己判断：

```
路径中的关键词 → 模块归属判断
  路径包含 /assets/       → 资产管理模块
  路径包含 /threat/       → 威胁分析模块
  路径包含 /auth/         → 权限认证模块
  路径包含 /controller/   → API/接口层
  路径包含 /service/      → 业务逻辑层
  路径包含 /repo/ 或 /dao/ → 数据访问层
  路径包含 /entity/       → 数据模型
  路径包含 /frontend/     → 前端模块
  路径包含 /mobile/       → 移动端模块
  ...（依靠你的常识判断）
```

如果路径模式不明确，可以根据文件名、目录深度、项目命名惯例综合判断。

### 规则 3：技术栈识别（从文件路径 + commit body 推断）

脚本不会告诉你用了什么技术。你需要自己从以下信息推断：

**从文件路径推断（主要来源）**：
```
路径特征 → 技术栈判断
  .java          → Java
  .py            → Python
  .js / .ts / .jsx / .tsx → JavaScript/TypeScript/React
  /service/      → 可能用了 Spring Service / Django Service
  /repo/ /dao/   → 可能用了 JPA / Hibernate / MyBatis
  /task/         → 可能用了 Spring Scheduled / Celery
  /controller/   → REST API 框架
  Dockerfile     → Docker
  deployment.yaml → Kubernetes
  package.json   → Node.js / npm
  pom.xml        → Maven / Java
```

**从 commit body 推断（辅助）**：
```
body 中的关键词 → 技术栈判断
  "CompletableFuture"    → Java 并发 / CompletableFuture
  "ExecutorService"      → 线程池
  "Pattern.compile"      → 正则表达式
  "async/await"          → Python/JS 异步
  "Redis"                → 缓存 / Redis
  "Kafka" / "RabbitMQ"   → 消息队列
  "docker" / "container" → 容器化
```

**重要**：如果一个技术名出现在 body 中，大概率是在这次提交中用到了它。

### 规则 4：问题推断（从 commit 标题 + body + 变更规模反推）

脚本不会告诉你这次提交解决了什么问题。你需要自己推断：

```
标题前缀 → 问题类型（参考）
  fix:    → 缺陷修复。从 body 找具体缺陷表现
  feat:   → 功能新增。从 body 找业务需求背景
  perf:   → 性能优化。从 body 找性能瓶颈描述
  refactor → 代码重构。从 body 找架构问题

推断方法（以 fix 为例）：
  title: "fix: 浪潮云主机OS字段解析全面修复"
  body: "新增 parseOsInfo() 方法，支持 V 前缀/无 V 前缀/Windows 格式..."
  推断：OS 字段格式多样（至少 3 种格式），现有硬编码方案无法适配，
        导致数据入库错误。需要设计通用解析方案。

推断技巧：
  - 从 "新增 XX 方法" → 之前缺少独立解析逻辑
  - 从 "支持 XX 格式" → 之前不支持这些格式
  - 从 "修复 XX 异常" → 之前存在边界情况未覆盖
  - 代码行数多 → 问题复杂度高
  - 涉及核心模块文件 → 问题影响面广
```

### 规则 5：方案提取（从代码变更模式反推设计思路）

```
变更模式 → 设计思路
  新增独立方法/类    → 模块化设计，关注点分离
  新增条件判断/兜底   → 防御性编程，容错设计
  引入线程池/异步调用 → 并发优化，资源隔离
  新增正则表达式解析   → 自适应解析，格式抽象
  添加缓存层         → 性能优化，减少重复计算
  修改 SQL/ORM 映射  → 数据一致性，查询优化
  新增接口/抽象类    → 面向接口设计，可扩展性

可以从 body 中的关键词辅助判断：
  "兜底" / "fallback"    → 防御性策略
  "并发" / "async"       → 异步并发
  "去重" / "dedup"       → 数据一致性
  "缓存" / "cache"       → 性能优化
  "限流" / "降级"        → 系统稳定性
```

### 规则 6：成果量化

尽可能给出具体数字。以下数据可从 JSON 中直接获取：

```
可从脚本输出直接获取的量化数据：
  - 代码新增行数     → summary.total_lines_added
  - 代码删除行数     → summary.total_lines_deleted
  - 提交次数         → summary.total_commits
  - 修改文件数       → summary.total_files_changed
  - 时间跨度         → summary.date_range

需要你估算的量化数据：
  - 性能提升百分比   → 从 "优化"、"并发" 等关键词估算（通常 30-50%）
  - 覆盖格式/模块数  → 从文件列表和 body 描述统计
  - bug 修复数       → 统计 fix: 类型提交
  - 功能覆盖度       → 从模块分布推断
```

---

## 第三步：输出模板

### 模板 A：求职简历（Resume）

每个项目成就 3-5 行，动词开头，包含量化指标：

```markdown
### [项目/功能名称]

**时间**：YYYY-MM ~ YYYY-MM | **代码量**：N 次提交，N+ 行

• [动词] [技术/方案] [具体应用]，[量化成果]
• [动词] [技术/方案] [具体应用]，[量化成果]
• [动词] [技术/方案] [具体应用]，[量化成果]

**技术栈**：[核心技术 3-5 个]
```

**动词库**：设计、实现、优化、重构、诊断、修复、重构、迁移、集成、构建

### 模板 B：面试讲稿（STAR 法则）

2-3 分钟的项目讲解：

```markdown
## [项目名称]（讲稿）

**大背景**（Situation）：[业务背景]

**核心问题**（Task）：
1. [问题 1：现象 + 根因]
2. [问题 2：现象 + 根因]

**我的方案**（Action）：
- [方案 1：设计思路]
- [方案 2：技术亮点]

**成果量化**（Result）：
- [量化指标]
```

### 模板 C：技术文章（Blog）

适用于博客或项目总结：

```markdown
# [技术总结] [项目名称]

## 问题分析
[现象 → 根因 → 影响]

## 方案对比
[方案 A vs 方案 B，为什么这样选]

## 实现细节
[核心逻辑 + 关键代码]

## 量化效果
[性能/质量提升数据]
```

---

## 完整工作流程示例

假设你要分析作者 luoxiaogen 在项目中的产出。以下是你实际应该做的每一步：

### 第 1 步：看提交历史概览

```bash
git log --author="luoxiaogen" --all --oneline --no-merges
```

输出：
```
58c58df fix(assets): 浪潮云主机OS字段解析全面修复
6c0539b fix: 更新统计栏永中office统计逻辑
372fbe2 fix(assets): 浪潮云主机OS字段解析及CPU硬件非空约束修复
f203495 fix: mergeTerminal中对mac_addr空值兜底为空字符串
6d9d105 feat: 360办公终端software接口支持全量分页并发拉取
f8893ba feat: 360办公终端software接口支持全量分页并发拉取
c7ae44a fix(threat): 修正getManagerPerson Tuple别名映射
18b5d75 多结果歧义时不绑定资产信息
15535de 资产匹配IP查询由模糊匹配改为精确匹配
bee0032 资产匹配IP查询由模糊匹配改为精确匹配
c4711bb 优化办公终端数据处理逻辑，增加去重和冲突合并功能
c5fd07e 优化办公终端360数据同步逻辑
```

### 第 2 步：看关键提交的 diff（核心步骤！）

不要只看标题。挑出代码量大的提交，看实际改了啥：

```bash
# OS 字段解析——看看到底怎么解析的
git show 58c58df

# 看到新增了 parseOsInfo() 方法
# 看到 Pattern.compile() 多格式匹配
# 看到 null 保护逻辑
```

通过 diff 你能发现：
- 删掉了什么旧代码（通常是硬编码的 if-else）
- 新增了什么设计（正则匹配、枚举扩展）
- 有没有防御性处理（null 检查、异常捕获）
- 涉及哪些类和方法（推断架构层级）

### 第 3 步：看源码理解上下文

```bash
# 看整个模块的结构
ls assets/src/main/java/com/cqcdi/ngsoc/assets/

# 读关键文件
cat assets/src/main/java/com/cqcdi/ngsoc/assets/service/impl/AMachineServiceImpl.java
```

从源码你可以确认：
- 项目的技术栈（Spring Boot? JPA? MyBatis?）
- 代码质量水平
- 架构设计模式
- 模块间的依赖关系

### 第 4 步：综合分析与合并

现在你掌握了所有信息，开始合并逻辑：

```
OS 字段解析（2 次提交，+133 行）
  ├─ 58c58df: 全面修复，新增 parseOsInfo() 方法
  └─ 372fbe2: CPU 非空约束修复
  → 合并为「多格式 OS 字段解析引擎」

并发拉取（2 次提交，+345 行）
  ├─ 6d9d105: 首次实现分页并发
  └─ f8893ba: 完善和修复
  → 合并为「终端数据全量并发拉取优化」

资产查询（3 次提交，+25 行）
  ├─ 15535de: 模糊→精确匹配
  ├─ bee0032: 补充完善
  └─ 18b5d75: 多结果去歧义
  → 合并为「资产匹配查询优化」
```

### 第 5 步：撰写简历

```markdown
### 资产管理系统数据集成优化

**时间**：2026-04 ~ 2026-05 | **代码量**：12 次提交，1,375+ 行

• 设计并实现多操作系统类型自适应字段解析引擎，
  使用正则表达式支持 5+ 种格式自动识别和转换，
  防御性设计确保异常情况下数据不被覆盖
• 使用 CompletableFuture + ExecutorService 实现
  终端数据全量分页并发拉取，性能提升约 40%
• 诊断并修复 JPA ORM 映射问题和数据库约束冲突，
  优化资产匹配查询算法，提升数据一致性

**技术栈**：Java、Spring Boot、JPA/Hibernate、CompletableFuture、正则表达式
```

---

## 最佳实践

### ✅ 应该这样做

- **先看 JSON 全貌**：了解提交数量、时间跨度、代码规模
- **按功能合并提交**：一个 feature 可能跨 2-5 次提交
- **从路径识技术**：文件路径是技术栈的最可靠信号
- **从不确到确定**：body 中提到的技术名 → 大概率使用了
- **量化优先**：有数字用数字，没数字用估算（说明是估算）

### ❌ 避免这样做

- **逐条罗列 commit**：简历不是 git log
- **编造不存在的技术**：文件路径和 body 都没提到的技术不要写
- **模糊表述**："做了优化"→"查询性能提升约 40%"
- **堆砌技术栈**：控制在 8 个以内，只说核心的

### 质量检查清单

- [ ] Merge commit 已过滤
- [ ] 相同功能的提交已合并
- [ ] 技术栈都有路径或 body 依据
- [ ] 问题描述有根因分析（不只是症状）
- [ ] 量化指标尽量使用脚本输出的数据
- [ ] 语言专业、动词开头
