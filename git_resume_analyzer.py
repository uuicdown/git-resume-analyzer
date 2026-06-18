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
import json
import os
import sys
from typing import List, Dict
import argparse


class GitDataCollector:
    """Git 数据采集器——只做机械的数据提取，不做任何语义推断"""

    def __init__(self, author: str, since: str = None, until: str = None):
        self.author = author
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
        """获取提交数据，返回纯结构化信息"""
        args = ['git', 'log', f'--author={self.author}', '--all',
                '--format=%h|%ai|%s|%B', '--numstat']
        if self.since:
            args.append(f'--since={self.since}')
        if self.until:
            args.append(f'--until={self.until}')

        output = self._run_git(args)
        if not output:
            return []

        commits = []
        current = None

        for line in output.split('\n'):
            if '|' in line and not line.startswith('\t'):
                # 提交头行
                if current:
                    commits.append(current)
                parts = line.split('|', 3)
                current = {
                    'hash': parts[0],
                    'date': parts[1].split()[0] if len(parts) > 1 else '',
                    'title': parts[2] if len(parts) > 2 else '',
                    'body': parts[3] if len(parts) > 3 else '',
                    'files': [],
                    'lines_added': 0,
                    'lines_deleted': 0,
                    'is_merge': parts[2].startswith('Merge') if len(parts) > 2 else False,
                }
            elif current and line and not line.startswith('|'):
                # numstat 行
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        added = int(parts[0]) if parts[0].lstrip('-').isdigit() else 0
                        deleted = int(parts[1]) if parts[1].lstrip('-').isdigit() else 0
                        current['lines_added'] += added
                        current['lines_deleted'] += deleted
                        current['files'].append(parts[2])
                    except (ValueError, IndexError):
                        pass

        if current:
            commits.append(current)

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
                'author': self.author,
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
            'author': self.author,
            'total_commits': len(self.commits),
            'merge_commits': merge_count,
            'total_lines_added': sum(c['lines_added'] for c in self.commits),
            'total_lines_deleted': sum(c['lines_deleted'] for c in self.commits),
            'total_files_changed': len(all_files),
            'date_range': f"{dates[-1]} ~ {dates[0]}" if len(dates) >= 2 else (dates[0] if dates else 'N/A'),
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
        lines.append(f"作者：{self.author}")
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
        """,
    )
    parser.add_argument('--author', required=True, help='Git 作者名称')
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
