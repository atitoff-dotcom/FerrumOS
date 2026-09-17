import os
import sys
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent

def test_powershell():
    print("Testing tools/install.ps1...")
    # On Linux/macOS pwsh is used; on Windows both pwsh and powershell are supported
    ps_bin = shutil.which("pwsh") or shutil.which("powershell")
    if not ps_bin:
        print("  [SKIP] Neither 'pwsh' nor 'powershell' found.")
        return

    res = subprocess.run(
        [ps_bin, "-ExecutionPolicy", "Bypass", "-File", str(ROOT_DIR / "tools" / "install.ps1"), "-DryRun"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    assert res.returncode == 0, f"PowerShell failed with code {res.returncode}:\n{res.stderr}\n{res.stdout}"
    assert "[DryRun]" in res.stdout, "DryRun marker not found in output"
    print(f"  [OK] PowerShell install.ps1 -DryRun passed (using {Path(ps_bin).name}).")

def test_bash():
    print("Testing tools/install.sh...")
    bash_bin = None
    if os.name == "nt":
        # Avoid C:\Windows\System32\bash.exe (WSL wrapper without distro)
        for cand in [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files\Git\usr\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
        ]:
            if os.path.exists(cand):
                bash_bin = cand
                break
    else:
        bash_bin = shutil.which("bash")

    if not bash_bin:
        print("  [SKIP] Real 'bash' binary not found.")
        return

    # 1. Syntax validation
    res = subprocess.run([bash_bin, "-n", str(ROOT_DIR / "tools" / "install.sh")], capture_output=True, text=True)
    assert res.returncode == 0, f"Bash syntax error:\n{res.stderr}"
    print(f"  [OK] Bash install.sh syntax valid (using {Path(bash_bin).name}).")

    # 2. DryRun test (runs on real Linux / macOS)
    if os.name != "nt":
        res = subprocess.run([bash_bin, str(ROOT_DIR / "tools" / "install.sh"), "--dry-run"], capture_output=True, text=True)
        assert res.returncode == 0, f"Bash dry-run failed with code {res.returncode}:\n{res.stderr}\n{res.stdout}"
        assert "[DryRun]" in res.stdout, "DryRun marker not found in output"
        print(f"  [OK] Bash install.sh --dry-run passed (using {Path(bash_bin).name}).")
    else:
        print("  [SKIP] Skipping install.sh execution on Windows (Linux/macOS target).")

if __name__ == "__main__":
    test_powershell()
    test_bash()
    print("✨ All installer tests passed successfully!")
