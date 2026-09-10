#!/usr/bin/env python3
"""git_resume_analyzer.py 的回归测试。

覆盖三个曾经踩过的解析坑（对应 git_resume_analyzer.py 里 fetch_commits 的修复）：

  1. commit body 多行或含 '|' 时，记录被撕裂 / 字段错位
  2. --numstat 的文件统计被多行 body 污染
  3. 标题不含 "Merge" 的合并提交被漏判（应靠父提交数判断）

运行（用任意 Python 3.7+）：

    python test_git_resume.py

脚本会在系统临时目录建一个一次性的 git 仓库，构造上述场景，调用
git_resume_analyzer.py 并断言输出；跑完自动清理。需要 git 在 PATH 上。
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYZER = os.path.join(HERE, "git_resume_analyzer.py")
AUTHOR = "Test User"
PIPE_TITLE = "fix: 解析管道符|的兼容"
PIPE_BODY_LINE = "第二行含|符号，验证不分裂"
MERGE_TITLE = "合并功能分支到主干"


def run_git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True, encoding="utf-8"
    )


def make_temp_repo_dir():
    """建一个确实可写的临时目录。依次尝试环境变量、系统 TEMP、脚本目录，
    真正写一个探测文件确认可写后才采用。

    故意不用 tempfile.mkdtemp：它以 0o700 权限建目录，在受限 ACL 环境下
    可能“建得出目录却写不进文件”；os.makedirs 用默认权限没这个问题。
    """
    candidates = []
    env_dir = os.environ.get("GRA_TEST_TMPDIR")
    if env_dir:
        candidates.append(env_dir)
    candidates.append(tempfile.gettempdir())
    candidates.append(HERE)
    last_err = None
    for d in candidates:
        try:
            os.makedirs(d, exist_ok=True)
            probe = os.path.join(d, f"gra-test-{os.getpid()}-{int(time.time() * 1000)}")
            os.makedirs(probe, exist_ok=True)
            with open(os.path.join(probe, ".probe"), "w", encoding="utf-8") as f:
                f.write("x")
            os.remove(os.path.join(probe, ".probe"))
            return probe
        except OSError as e:
            last_err = e
    raise last_err


class GitResumeAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("git") is None:
            raise unittest.SkipTest("git not found on PATH")

        cls.repo = make_temp_repo_dir()
        run_git(cls.repo, "init", "-q")
        run_git(cls.repo, "config", "user.email", "test@example.com")
        run_git(cls.repo, "config", "user.name", AUTHOR)
        run_git(cls.repo, "config", "commit.gpgsign", "false")

        # commit 1: 普通提交
        cls._write("a.txt", "a")
        run_git(cls.repo, "add", "a.txt")
        run_git(cls.repo, "commit", "-q", "-m", "feat: 基础功能")

        # commit 2: 标题含 '|'，body 多行且含 '|' —— 触发坑 1 和 2
        cls._write("b.txt", "b")
        run_git(cls.repo, "add", "b.txt")
        run_git(
            cls.repo, "commit", "-q",
            "-m", PIPE_TITLE,
            "-m", "第一行\n" + PIPE_BODY_LINE,
        )

        # commit 3: 普通提交
        cls._write("c.txt", "c")
        run_git(cls.repo, "add", "c.txt")
        run_git(cls.repo, "commit", "-q", "-m", "perf: 优化查询")

        # 分支 + merge（双父提交，但标题不含 "Merge"）—— 触发坑 3
        run_git(cls.repo, "checkout", "-q", "-b", "feature")
        cls._write("d.txt", "d")
        run_git(cls.repo, "add", "d.txt")
        run_git(cls.repo, "commit", "-q", "-m", "feat: 功能分支")
        run_git(cls.repo, "checkout", "-q", "-")
        run_git(cls.repo, "merge", "--no-ff", "feature", "-q", "-m", MERGE_TITLE)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "repo"):
            shutil.rmtree(cls.repo, ignore_errors=True)

    @classmethod
    def _write(cls, name, content):
        with open(os.path.join(cls.repo, name), "w", encoding="utf-8") as f:
            f.write(content)

    def _analyze(self, *extra):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        out = subprocess.run(
            [sys.executable, ANALYZER, "--author", AUTHOR, "--json", *extra],
            cwd=self.repo, capture_output=True, text=True,
            encoding="utf-8", env=env,
        )
        self.assertEqual(out.returncode, 0, msg=f"analyzer failed: {out.stderr}")
        return json.loads(out.stdout)

    # ---- 坑 1 & 2：含 '|' 的多行 body 不被撕裂，统计不被污染 ----

    def test_pipe_title_not_split(self):
        data = self._analyze()
        titles = [c["title"] for c in data["commits"]]
        self.assertIn(PIPE_TITLE, titles, "标题含 '|' 的提交被撕裂或丢失")

    def test_pipe_body_preserved_and_stats_clean(self):
        data = self._analyze()
        target = next(
            (c for c in data["commits"] if c["title"] == PIPE_TITLE), None
        )
        self.assertIsNotNone(target, "找不到含 '|' 的提交")
        # body 多行完整保留
        self.assertIn(PIPE_BODY_LINE, target["body"])
        # 统计只归属 b.txt，未被 body 行污染
        self.assertEqual(target["files"], ["b.txt"])
        self.assertEqual(target["lines_added"], 1)
        self.assertEqual(target["lines_deleted"], 0)

    # ---- 坑 3：靠父提交数识别 merge，而非标题 ----

    def test_merge_detected_by_parents(self):
        data = self._analyze()
        merges = [c for c in data["commits"] if c["is_merge"]]
        self.assertEqual(len(merges), 1, "merge 提交数量不对")
        self.assertEqual(merges[0]["title"], MERGE_TITLE)

    def test_no_merges_filters_out(self):
        full = self._analyze()
        filtered = self._analyze("--no-merges")
        self.assertEqual(
            len(full["commits"]) - len(filtered["commits"]), 1,
            "--no-merges 应恰好过滤掉 1 个 merge",
        )
        self.assertTrue(all(not c["is_merge"] for c in filtered["commits"]))

    # ---- 总量正确性 ----

    def test_totals(self):
        data = self._analyze("--no-merges")
        # 4 个非 merge 提交，各新增 1 文件 1 行
        self.assertEqual(data["summary"]["total_commits"], 4)
        self.assertEqual(data["summary"]["total_files_changed"], 4)
        self.assertEqual(data["summary"]["total_lines_added"], 4)
        self.assertEqual(data["summary"]["total_lines_deleted"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
