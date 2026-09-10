#!/usr/bin/env python3
"""
Git Resume Analyzer - 从 git 提交历史采集结构化数据

【分工】
  脚本 → 纯数据采集。跑 git log，输出结构化数据（JSON / 统计摘要）。
  AI   → 深度分析。基于脚本输出的数据，推断问题、技术栈、方案、成果。

【使用方式】
    python git_resume_analyzer.py --author "你的名字" --json
    python git_resume_analyzer.py --author "你的名字" --json --no-merges --output data.json
    python git_resume_analyzer.py --author "你的名字" --since "2026-04-01" --top-n 10
"""

import subprocess
import re
import json
import os
import sys
from typing import List, Dict
import argparse


class GitDataCollector:
    """Git 数据采集器——只做机械的数据提取，不做任何语义推断"""

    def __init__(self, authors, since: str = None, until: str = None):
        if isinstance(authors, str):
            authors = [authors]
        self.authors = list(authors) if authors else []
        self.since = since
        self.until = until
        self.commits: List[Dict] = []
        self._merge_filtered: int = 0  # 记录被 --no-merges 过滤掉的提交数

    # ---------- Git 命令执行 ----------

    def _run_git(self, args: List[str]) -> str:
        """执行 git 命令，用列表传参避免注入"""
        try:
            result = subprocess.run(args, capture_output=True, text=False, check=False)
            # 尝试多种编码解码
            for enc in ['utf-8', 'gbk', 'gb18030']:
                try:
                    stdout = result.stdout.decode(enc)
                    if result.returncode != 0:
                        stderr = result.stderr.decode(enc).strip()
                        if stderr:
                            print(f"Git 警告 (code={result.returncode}): {stderr}", file=sys.stderr)
                    return stdout.strip()
                except (UnicodeDecodeError, AttributeError):
                    continue
            return result.stdout.decode('utf-8', errors='replace').strip()
        except FileNotFoundError:
            print("未找到 git 命令，请确保已安装 Git", file=sys.stderr)
            return ""
        except Exception as e:
            print(f"执行 git 命令出错: {e}", file=sys.stderr)
            return ""

    # ---------- 数据采集 ----------

    def fetch_commits(self, no_merges: bool = False) -> List[Dict]:
        """获取提交数据，返回纯结构化信息。

        元数据与文件统计分两条 git log 采集：
        - 元数据用不可打印字符作为字段/记录分隔符（commit body 中不可能出现），
          避免 body 多行或含 '|' 时破坏解析；merge 用父提交数判断，不依赖标题。
        - 文件统计用 --numstat + %H 按 hash 关联，避免与多行 body 混在一起。
        """
        commits = []

        # ---- 命令 A：提交元数据 ----
        # %P 父提交列表；字段用 %x1f 分隔，body 放最后一段整体保留；记录用 %x1e 分隔。
        meta_args = ['git', 'log', '--all',
                     '--format=%P%x1f%H%x1f%ai%x1f%s%x1f%B%x1e']
        for a in self.authors:
            meta_args.append(f'--author={a}')
        if self.since:
            meta_args.append(f'--since={self.since}')
        if self.until:
            meta_args.append(f'--until={self.until}')

        meta_output = self._run_git(meta_args)
        if not meta_output:
            return []

        for record in meta_output.split('\x1e'):
            if not record.strip():
                continue
            fields = record.split('\x1f', 4)  # body 作为最后一段，含换行/分隔符也能完整保留
            if len(fields) < 5:
                continue
            parents = fields[0].split()
            commits.append({
                'hash': fields[1],
                'date': fields[2].split()[0] if fields[2] else '',
                'title': fields[3],
                'body': fields[4].rstrip(),
                'files': [],
                'lines_added': 0,
                'lines_deleted': 0,
                'is_merge': len(parents) > 1,
            })

        # ---- 命令 B：文件统计（按 hash 关联到元数据） ----
        stat_args = ['git', 'log', '--all', '--format=%H', '--numstat']
        for a in self.authors:
            stat_args.append(f'--author={a}')
        if self.since:
            stat_args.append(f'--since={self.since}')
        if self.until:
            stat_args.append(f'--until={self.until}')

        stat_output = self._run_git(stat_args)
        commit_map = {c['hash']: c for c in commits}
        current_hash = None
        if stat_output:
            for line in stat_output.split('\n'):
                if not line.strip():
                    continue
                if re.match(r'^[\d-]+\t[\d-]+\t', line):
                    parts = line.split('\t')
                    if len(parts) >= 3 and current_hash in commit_map:
                        target = commit_map[current_hash]
                        try:
                            added = int(parts[0]) if parts[0].lstrip('-').isdigit() else 0
                            deleted = int(parts[1]) if parts[1].lstrip('-').isdigit() else 0
                            target['lines_added'] += added
                            target['lines_deleted'] += deleted
                            target['files'].append(parts[2])
                        except (ValueError, IndexError):
                            pass
                else:
                    current_hash = line.strip()

        # 过滤 merge
        if no_merges:
            before = len(commits)
            commits = [c for c in commits if not c['is_merge']]
            self._merge_filtered = before - len(commits)

        self.commits = commits
        return commits

    # ---------- 统计摘要（纯数字，无推断） ----------

    def get_summary(self) -> Dict:
        """返回纯统计信息，不做任何语义分析"""
        if not self.commits:
            return {
                'author': ', '.join(self.authors),
                'total_commits': 0,
                'total_lines_added': 0,
                'total_lines_deleted': 0,
                'merge_commits': 0,
                'date_range': 'N/A',
                'total_files_changed': 0,
            }

        merge_count = sum(1 for c in self.commits if c['is_merge'])
        all_files = set()
        for c in self.commits:
            all_files.update(c['files'])

        dates = [c['date'] for c in self.commits if c['date']]

        return {
            'author': ', '.join(self.authors),
            'total_commits': len(self.commits),
            'merge_commits': merge_count,
            'total_lines_added': sum(c['lines_added'] for c in self.commits),
            'total_lines_deleted': sum(c['lines_deleted'] for c in self.commits),
            'total_files_changed': len(all_files),
            'date_range': f"{min(dates)} ~ {max(dates)}" if len(dates) >= 2 else (dates[0] if dates else 'N/A'),
        }

    # ---------- 输出 ----------

    def to_json(self, top_n: int = None) -> str:
        """输出完整 JSON（结构化的原始数据 + 统计摘要）"""
        commits_data = self.commits
        if top_n and top_n > 0:
            commits_data = self.commits[:top_n]

        return json.dumps({
            'summary': self.get_summary(),
            'commits': commits_data,
        }, ensure_ascii=False, indent=2)

    def print_summary(self, top_n: int = None) -> str:
        """输出可读的文本摘要，纯统计无推断"""
        summary = self.get_summary()
        if summary['total_commits'] == 0:
            return "没有找到提交记录，请检查作者名称是否正确。"

        lines = []
        lines.append(f"作者：{', '.join(self.authors)}")
        lines.append(f"时间：{summary['date_range']}")
        merge_info = f"（其中 merge {summary['merge_commits']} 次"
        if self._merge_filtered > 0:
            merge_info += f"，已过滤 {self._merge_filtered} 个 merge 提交"
        merge_info += "）"
        lines.append(f"提交：{summary['total_commits']} 次{merge_info}")
        lines.append(f"新增：{summary['total_lines_added']:,} 行")
        lines.append(f"删除：{summary['total_lines_deleted']:,} 行")
        lines.append(f"文件：{summary['total_files_changed']} 个")
        lines.append("")

        # 列出提交
        limit = top_n if top_n and top_n > 0 else len(self.commits)
        lines.append(f"提交列表（前 {min(limit, len(self.commits))} 条）：")
        for c in self.commits[:limit]:
            merge_tag = " [merge]" if c['is_merge'] else ""
            lines.append(f"  [{c['hash']}] {c['date']}{merge_tag} {c['title']}")
            if c['lines_added'] > 0 or c['lines_deleted'] > 0:
                lines.append(f"       +{c['lines_added']} / -{c['lines_deleted']} 行  {len(c['files'])} 个文件")

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Git Resume Analyzer — 从 git 提交历史采集结构化数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python git_resume_analyzer.py --author "张三"
  python git_resume_analyzer.py --author "张三" --json
  python git_resume_analyzer.py --author "张三" --json --no-merges --output data.json
  python git_resume_analyzer.py --author "张三" --since 2026-01-01 --no-merges
  python git_resume_analyzer.py --author "张三" --author "李四" --json   # 合并多个作者
        """,
    )
    parser.add_argument('--author', required=True, action='append',
                       help='Git 作者名称（可多次传入，合并多个作者）')
    parser.add_argument('--since', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--until', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--no-merges', action='store_true', help='过滤 Merge commit')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式（供 AI 分析）')
    parser.add_argument('--output', help='输出到文件')
    parser.add_argument('--top-n', type=int, default=None, help='限制输出的 commit 数量')

    args = parser.parse_args()

    collector = GitDataCollector(args.author, args.since, args.until)
    collector.fetch_commits(no_merges=args.no_merges)

    if args.json:
        result = collector.to_json(top_n=args.top_n)
    else:
        result = collector.print_summary(top_n=args.top_n)

    if args.output:
        out_dir = os.path.dirname(os.path.abspath(args.output))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"已生成到：{args.output}")
    else:
        print(result)


if __name__ == '__main__':
    main()
