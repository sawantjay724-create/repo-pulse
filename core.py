"""Core logic: read git history and compute statistics (standard library only)."""
from __future__ import annotations

import subprocess
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone

SEP = "\x1f"
MARK = "@@COMMIT@@"
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class GitError(RuntimeError):
    """Raised when git fails or the path is not a repository."""


@dataclass
class Commit:
    sha: str
    author: str
    timestamp: int
    files: list[str] = field(default_factory=list)

    @property
    def when(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp, tz=timezone.utc)


def load_commits(repo: str = ".", since: str | None = None) -> list[Commit]:
    """Return commits (newest first) with the files each one touched."""
    cmd = ["git", "-C", repo, "log", f"--pretty=format:{MARK}%H{SEP}%an{SEP}%at", "--name-only"]
    if since:
        cmd.append(f"--since={since}")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc
    except subprocess.CalledProcessError as exc:
        raise GitError(exc.stderr.strip() or "not a git repository") from exc
    return parse_log(out)


def parse_log(raw: str) -> list[Commit]:
    commits: list[Commit] = []
    for block in raw.split(MARK):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        sha, author, ts = lines[0].split(SEP)
        commits.append(Commit(sha, author, int(ts), lines[1:]))
    return commits


def commits_by_author(commits: list[Commit]) -> list[tuple[str, int]]:
    return Counter(c.author for c in commits).most_common()


def commits_by_weekday(commits: list[Commit]) -> dict[str, int]:
    counts = Counter(c.when.weekday() for c in commits)
    return {name: counts.get(i, 0) for i, name in enumerate(WEEKDAYS)}


def hotspots(commits: list[Commit], top: int = 10) -> list[tuple[str, int]]:
    """Files changed most often: frequent churn often marks fragile code."""
    return Counter(f for c in commits for f in c.files).most_common(top)


def bus_factor(commits: list[Commit]) -> int:
    """Smallest number of authors who together made over 50% of the commits."""
    total = len(commits)
    if total == 0:
        return 0
    covered = 0
    for n, (_, count) in enumerate(commits_by_author(commits), start=1):
        covered += count
        if covered * 2 > total:
            return n
    return 0


def summarize(commits: list[Commit], top: int = 10) -> dict:
    return {
        "total_commits": len(commits),
        "authors": commits_by_author(commits),
        "weekdays": commits_by_weekday(commits),
        "hotspots": hotspots(commits, top),
        "bus_factor": bus_factor(commits),
    }
