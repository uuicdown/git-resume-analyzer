# Git Resume Analyzer 输出示例

以下是用脚本生成的 JSON 数据示例。可作快速参考，但深度分析仍建议 AI 直接查看 diff 和源码。

## 命令

```bash
python git_resume_analyzer.py --author "luoxiaogen" --json --no-merges
```

## 输出

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
      "body": "fix(assets): 浪潮云主机OS字段解析全面修复\n\n1. 新增 parseOsInfo() 方法，解析浪潮推送的组合 os_type 字符串\n2. 支持 V 前缀格式（linux-Kylin-Server-V10-SP3-2303-ARM64）\n3. 支持无 V 前缀格式（kylin10sp2arm）通过 kylin<N> 兜底\n4. 支持 Windows 格式（Windows 2019 数据中心版 中文版 64位）\n5. osVersion 改为发行版全名：Windows 完整保留，Linux/麒麟去 linux-前缀和 -SP 后缀\n6. 内核版本正则仅在非 Windows 系统执行，避免误匹配年份\n7. OS 字段设置增加空值保护，解析为空时不覆盖数据库已有有效值\n8. osTypeMap、machineOsTypeList 新增麒麟选项",
      "files": [
        "assets/src/main/java/com/cqcdi/ngsoc/assets/service/impl/AMachineServiceImpl.java",
        "common/src/main/java/com/cqcdi/ngsoc/common/utils/Constant.java"
      ],
      "lines_added": 79,
      "lines_deleted": 7,
      "is_merge": false
    },
    {
      "hash": "372fbe2",
      "date": "2026-05-13",
      "title": "fix(assets): 浪潮云主机OS字段解析及CPU硬件非空约束修复",
      "body": "fix(assets): 浪潮云主机OS字段解析及CPU硬件非空约束修复\n\n1. 新增 parseOsInfo() 方法，解析并分割浪潮推送的组合 os_type 字符串\n2. 修复 saveMachineHardware() 中 CPU 保存时 hardwareModel 未赋值导致非空约束异常\n3. 机器操作系统枚举列表、osTypeMap 新增麒麟选项",
      "files": [
        "assets/src/main/java/com/cqcdi/ngsoc/assets/service/impl/AMachineServiceImpl.java",
        "common/src/main/java/com/cqcdi/ngsoc/common/utils/Constant.java"
      ],
      "lines_added": 54,
      "lines_deleted": 7,
      "is_merge": false
    },
    {
      "hash": "f203495",
      "date": "2026-05-12",
      "title": "fix: mergeTerminal中对mac_addr空值兜底为空字符串",
      "body": "fix: mergeTerminal中对mac_addr空值兜底为空字符串\n\nchooseBetterValue 两边均为 null 时返回 null，\n导致 mergeTerminal 将已设置的空字符串覆盖为 null，\n写入数据库时违反 NOT NULL 约束。",
      "files": [
        "assets/src/main/java/com/cqcdi/ngsoc/assets/service/impl/ATerminalServiceImpl.java"
      ],
      "lines_added": 6,
      "lines_deleted": 1,
      "is_merge": false
    },
    {
      "hash": "6d9d105",
      "date": "2026-05-09",
      "title": "feat: 360办公终端software接口支持全量分页并发拉取，优化拉取时间",
      "body": "feat: 360办公终端software接口支持全量分页并发拉取，优化拉取时间\n\n使用 CompletableFuture + ExecutorService 实现并发拉取。",
      "files": [
        "assets/src/main/java/com/cqcdi/ngsoc/assets/task/TerminalScheduledTask.java"
      ],
      "lines_added": 173,
      "lines_deleted": 147,
      "is_merge": false
    },
    {
      "hash": "c4711bb",
      "date": "2026-04-18",
      "title": "优化办公终端数据处理逻辑，增加去重和冲突合并功能",
      "body": "优化办公终端数据处理逻辑，增加去重和冲突合并功能，提升数据一致性和准确性",
      "files": [
        "assets/src/main/java/com/cqcdi/ngsoc/assets/service/impl/ATerminalServiceImpl.java",
        "assets/src/main/java/com/cqcdi/ngsoc/assets/repo/pg/ATerminalRepo.java"
      ],
      "lines_added": 849,
      "lines_deleted": 30,
      "is_merge": false
    },
    {
      "hash": "c7ae44a",
      "date": "2026-04-30",
      "title": "fix(threat): 修正getManagerPerson Tuple别名 snake_case 为 camelCase",
      "body": "fix(threat): 修正getManagerPerson Tuple别名 snake_case 为 camelCase",
      "files": [
        "threat/src/main/java/com/cqcdi/ngsoc/threat/service/impl/TAssetsThreatServiceImpl.java"
      ],
      "lines_added": 2,
      "lines_deleted": 2,
      "is_merge": false
    },
    {
      "hash": "15535de",
      "date": "2026-04-29",
      "title": "资产匹配IP查询由模糊匹配改为精确匹配",
      "body": "资产匹配IP查询由模糊匹配改为精确匹配",
      "files": [
        "threat/src/main/java/com/cqcdi/ngsoc/threat/repo/pg/TAssetsThreatRepo.java"
      ],
      "lines_added": 3,
      "lines_deleted": 3,
      "is_merge": false
    }
  ]
}
```

## AI 可以从中分析出什么

| 数据字段 | AI 能推断出的信息 |
|----------|----------------|
| `files` 路径中的 `/service/`、`/repo/`、`/task/` | 技术栈：Spring Service、JPA、Spring Scheduled |
| body 中的 "CompletableFuture"、"ExecutorService" | 并发编程技术 |
| body 中的 "parseOsInfo()"、"V 前缀格式" | 正则表达式解析引擎 |
| 文件扩展名 `.java`、目录结构 | Java / Maven 项目 |
| assets 和 threat 两大模块 | 模块划分 |
| 多个相关 commit | 可以合并为更大的项目成就 |
