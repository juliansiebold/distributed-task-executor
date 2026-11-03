import shutil
import subprocess

COMMAND = "distributed-task-executor"


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    executable = shutil.which(COMMAND)
    assert executable is not None, f"{COMMAND} is not installed"
    return subprocess.run([executable, *args], capture_output=True, text=True)


def test_help_lists_every_subcommand():
    result = run_command("--help")

    assert result.returncode == 0, result.stderr
    for subcommand in ("demo", "api", "worker", "watchdog"):
        assert subcommand in result.stdout


def test_unbuilt_subcommand_reports_failure():
    result = run_command("worker")

    assert result.returncode == 1
    assert "not implemented yet" in result.stderr
