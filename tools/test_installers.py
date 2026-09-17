import os
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def test_powershell_dry_run():
    print("Testing tools/install.ps1 -DryRun...")
    res = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ROOT_DIR / "tools" / "install.ps1"), "-DryRun"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    assert res.returncode == 0, f"PS failed:\n{res.stderr}\n{res.stdout}"
    assert "[DryRun]" in res.stdout, "DryRun marker not found in output"
    print("  [OK] PowerShell install.ps1 -DryRun passed.")

def test_bash_syntax():
    print("Testing tools/install.sh syntax...")
    bash_path = "C:/Program Files/Git/bin/bash.exe"
    if not Path(bash_path).exists():
        print("  [SKIP] Git Bash not found.")
        return
    res = subprocess.run([bash_path, "-n", str(ROOT_DIR / "tools" / "install.sh")], capture_output=True, text=True)
    assert res.returncode == 0, f"Bash syntax error:\n{res.stderr}"
    print("  [OK] Bash install.sh syntax valid.")

if __name__ == "__main__":
    test_powershell_dry_run()
    test_bash_syntax()
    print("All installer tests passed!")
