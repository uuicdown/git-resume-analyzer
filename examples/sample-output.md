# Git Resume Analyzer 输出示例

以下是用脚本生成的 JSON 数据示例。可作快速参考，但深度分析仍建议 AI 直接查看 diff 和源码。

## 命令

```bash
python git_resume_analyzer.py --author "alice" --json --no-merges
```

## 输出

```json
{
  "summary": {
    "author": "alice",
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
      "title": "fix(orders): 订单状态字段解析修复",
      "body": "fix(orders): 订单状态字段解析修复\n\n1. 新增 parseStatusInfo() 方法，解析第三方推送的组合状态字符串\n2. 支持带前缀格式\n3. 支持无前缀格式\n4. 状态值统一为规范名称\n5. 解析为空时不覆盖已有有效值\n6. statusMap、statusList 新增若干选项",
      "files": [
        "orders/src/main/java/com/example/app/orders/service/impl/OrderServiceImpl.java",
        "common/src/main/java/com/example/app/common/utils/Constant.java"
      ],
      "lines_added": 79,
      "lines_deleted": 7,
      "is_merge": false
    },
    {
      "hash": "372fbe2",
      "date": "2026-05-13",
      "title": "fix(orders): 订单状态字段解析及空值约束修复",
      "body": "fix(orders): 订单状态字段解析及空值约束修复\n\n1. 新增 parseStatusInfo() 方法，解析并分割第三方推送的组合状态字符串\n2. 修复字段未赋值导致非空约束异常\n3. 状态枚举列表、statusMap 新增选项",
      "files": [
        "orders/src/main/java/com/example/app/orders/service/impl/OrderServiceImpl.java",
        "common/src/main/java/com/example/app/common/utils/Constant.java"
      ],
      "lines_added": 54,
      "lines_deleted": 7,
      "is_merge": false
    },
    {
      "hash": "f203495",
      "date": "2026-05-12",
      "title": "fix: 合并订单时对空字段兜底为空字符串",
      "body": "fix: 合并订单时对空字段兜底为空字符串\n\nchooseBetterValue 两边均为 null 时返回 null，\n导致合并时将已设置的空字符串覆盖为 null，\n写入数据库时违反 NOT NULL 约束。",
      "files": [
        "orders/src/main/java/com/example/app/orders/service/impl/OrderServiceImpl.java"
      ],
      "lines_added": 6,
      "lines_deleted": 1,
      "is_merge": false
    },
    {
      "hash": "6d9d105",
      "date": "2026-05-09",
      "title": "feat: 库存数据接口支持全量分页并发拉取，优化拉取时间",
      "body": "feat: 库存数据接口支持全量分页并发拉取，优化拉取时间\n\n使用 CompletableFuture + ExecutorService 实现并发拉取。",
      "files": [
        "orders/src/main/java/com/example/app/orders/task/InventorySyncTask.java"
      ],
      "lines_added": 173,
      "lines_deleted": 147,
      "is_merge": false
    },
    {
      "hash": "c4711bb",
      "date": "2026-04-18",
      "title": "优化库存数据处理逻辑，增加去重和冲突合并功能",
      "body": "优化库存数据处理逻辑，增加去重和冲突合并功能，提升数据一致性和准确性",
      "files": [
        "orders/src/main/java/com/example/app/orders/service/impl/InventoryServiceImpl.java",
        "orders/src/main/java/com/example/app/orders/repo/pg/InventoryRepo.java"
      ],
      "lines_added": 849,
      "lines_deleted": 30,
      "is_merge": false
    },
    {
      "hash": "c7ae44a",
      "date": "2026-04-30",
      "title": "fix(users): 修正 getOwnerInfo Tuple 别名 snake_case 为 camelCase",
      "body": "fix(users): 修正 getOwnerInfo Tuple 别名 snake_case 为 camelCase",
      "files": [
        "users/src/main/java/com/example/app/users/service/impl/UserServiceImpl.java"
      ],
      "lines_added": 2,
      "lines_deleted": 2,
      "is_merge": false
    },
    {
      "hash": "15535de",
      "date": "2026-04-29",
      "title": "订单匹配查询由模糊匹配改为精确匹配",
      "body": "订单匹配查询由模糊匹配改为精确匹配",
      "files": [
        "users/src/main/java/com/example/app/users/repo/pg/UserRepo.java"
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
| body 中的 "parseStatusInfo()"、"前缀格式" | 正则表达式解析引擎 |
| 文件扩展名 `.java`、目录结构 | Java / Maven 项目 |
| orders 和 users 两大模块 | 模块划分 |
| 多个相关 commit | 可以合并为更大的项目成就 |
