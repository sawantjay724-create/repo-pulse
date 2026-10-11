import os
import subprocess

import pytest

from repo_pulse.cli import main
from repo_pulse.core import GitError, bus_factor, load_commits, summarize


def git(repo, *args, date=None, who="Alice"):
    env = {**os.environ, "GIT_AUTHOR_NAME": who, "GIT_COMMITTER_NAME": who,
           "GIT_AUTHOR_EMAIL": f"{who}@x.io", "GIT_COMMITTER_EMAIL": f"{who}@x.io"}
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", "-C", str(repo), *args], check=True, env=env, capture_output=True)


def commit(repo, filename, who, date):
    (repo / filename).write_text(f"{who}{date}")
    git(repo, "add", ".", who=who)
    git(repo, "commit", "-m", "c", date=date, who=who)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    commit(tmp_path, "a.py", "Alice", "2024-01-01T12:00:00+00:00")  # Monday
    commit(tmp_path, "a.py", "Alice", "2024-01-02T12:00:00+00:00")  # Tuesday
    commit(tmp_path, "b.py", "Alice", "2024-01-03T12:00:00+00:00")  # Wednesday
    commit(tmp_path, "a.py", "Bob", "2024-01-04T12:00:00+00:00")    # Thursday
    return tmp_path


def test_summary(repo):
    s = summarize(load_commits(str(repo)))
    assert s["total_commits"] == 4
    assert s["authors"][0] == ("Alice", 3)
    assert s["hotspots"][0] == ("a.py", 3)
    assert s["weekdays"]["Mon"] == 1 and s["weekdays"]["Sun"] == 0


def test_bus_factor(repo):
    assert bus_factor(load_commits(str(repo))) == 1
    assert bus_factor([]) == 0


def test_not_a_repo(tmp_path):
    with pytest.raises(GitError):
        load_commits(str(tmp_path))


def test_cli_json_and_text(repo, capsys):
    assert main([str(repo), "--json"]) == 0
    assert '"total_commits": 4' in capsys.readouterr().out
    assert main([str(repo)]) == 0
    assert "Hotspot files" in capsys.readouterr().out


def test_cli_error_exit_code(tmp_path, capsys):
    assert main([str(tmp_path)]) == 1
