"""Tests for bash_guard.py — run with: python3 -m unittest discover res-dev/hooks"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARD = Path(__file__).with_name("bash_guard.py")


def run_guard(command: str, cwd: str = "/tmp", tool: str = "Bash") -> subprocess.CompletedProcess:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"command": command},
        "cwd": cwd,
    }
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def make_repo(branch: str) -> str:
    repo = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", "-b", branch, repo], check=True)
    return repo


class CommitOnDefaultBranch(unittest.TestCase):
    def test_blocks_commit_on_master(self):
        r = run_guard('git commit -m "x"', cwd=make_repo("master"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("master", r.stderr)

    def test_blocks_commit_on_main(self):
        self.assertEqual(run_guard('git commit -m "x"', cwd=make_repo("main")).returncode, 2)

    def test_allows_commit_on_feature_branch(self):
        self.assertEqual(run_guard('git commit -m "x"', cwd=make_repo("feature/X-1-a")).returncode, 0)

    def test_respects_git_dash_c(self):
        repo = make_repo("master")
        self.assertEqual(run_guard(f'git -C {repo} commit -m "x"', cwd="/tmp").returncode, 2)

    def test_chained_command(self):
        self.assertEqual(run_guard('make test && git commit -m "x"', cwd=make_repo("main")).returncode, 2)

    def test_follows_cd_before_commit(self):
        repo = make_repo("master")
        self.assertEqual(run_guard(f'cd {repo} && git commit -m "x"', cwd=make_repo("feature/x")).returncode, 2)
        feature = make_repo("feature/x")
        self.assertEqual(run_guard(f'cd {feature} && git commit -m "x"', cwd=make_repo("main")).returncode, 0)

    def test_ignores_non_repo(self):
        self.assertEqual(run_guard('git commit -m "x"', cwd=tempfile.mkdtemp()).returncode, 0)


class AddAll(unittest.TestCase):
    def test_blocks_variants(self):
        for cmd in ["git add -A", "git add --all", "git add .", "git add -A frontend", "git commit -am 'x'"]:
            with self.subTest(cmd=cmd):
                self.assertEqual(run_guard(cmd, cwd=make_repo("feature/x")).returncode, 2)

    def test_allows_explicit_paths(self):
        for cmd in ["git add src/a.ts docs/b.md", "git add -p src/a.ts", "git add ./src/a.ts"]:
            with self.subTest(cmd=cmd):
                self.assertEqual(run_guard(cmd, cwd=make_repo("feature/x")).returncode, 0)


class Attribution(unittest.TestCase):
    def test_blocks_trailer_in_commit_message(self):
        cmd = 'git commit -m "feat: x\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"'
        self.assertEqual(run_guard(cmd, cwd=make_repo("feature/x")).returncode, 2)

    def test_blocks_footer_in_pr_body(self):
        cmd = 'gh pr create --title t --body "x\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)"'
        self.assertEqual(run_guard(cmd).returncode, 2)

    def test_blocks_trailer_in_body_file(self):
        f = Path(tempfile.mkdtemp()) / "msg.txt"
        f.write_text("feat: x\n\nco-authored-by: claude <noreply@anthropic.com>\n")
        self.assertEqual(run_guard(f"git commit -F {f}", cwd=make_repo("feature/x")).returncode, 2)
        self.assertEqual(run_guard(f"gh pr create --title t --body-file {f}").returncode, 2)

    def test_blocks_trailer_in_heredoc_message(self):
        cmd = (
            "git commit -m \"$(cat <<'EOF'\nfeat: x\n\nbody\n\n"
            "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nEOF\n)\""
        )
        self.assertEqual(run_guard(cmd, cwd=make_repo("feature/x")).returncode, 2)

    def test_allows_clean_heredoc_message(self):
        cmd = "git commit -m \"$(cat <<'EOF'\nfeat: x\n\nbody\nEOF\n)\""
        self.assertEqual(run_guard(cmd, cwd=make_repo("feature/x")).returncode, 0)

    def test_allows_human_coauthor(self):
        cmd = 'git commit -m "feat: x\n\nCo-Authored-By: Jane Doe <jane@example.com>"'
        self.assertEqual(run_guard(cmd, cwd=make_repo("feature/x")).returncode, 0)

    def test_ignores_mention_outside_commit_and_pr(self):
        self.assertEqual(run_guard('grep -r "Generated with Claude Code" .').returncode, 0)


class Passthrough(unittest.TestCase):
    def test_other_tools_and_commands(self):
        self.assertEqual(run_guard("ls -la").returncode, 0)
        self.assertEqual(run_guard("git status").returncode, 0)
        self.assertEqual(run_guard("git add -A", tool="Read").returncode, 0)

    def test_malformed_input_never_blocks(self):
        r = subprocess.run([sys.executable, str(GUARD)], input="not json", capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
