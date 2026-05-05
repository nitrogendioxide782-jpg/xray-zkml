# wsl_ezkl_runner.py
# 🔥 FINAL WINDOWS CP950 FIX
# 修正 UnicodeDecodeError（ezkl 的 UTF-8 emoji / symbols）

import subprocess

BASE = "/mnt/c/Users/liugu/xray-zkml"


def run_ezkl(cmd: str):

    full_cmd = f"""
    cd {BASE} &&
    source venv/bin/activate &&
    {cmd}
    """

    result = subprocess.run(
        ["wsl", "bash", "-lc", full_cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",   # ✅ 強制 UTF-8
        errors="ignore"     # ✅ 忽略 emoji / 特殊字元
    )

    print("📦 STDOUT:\n", result.stdout)
    print("📦 STDERR:\n", result.stderr)

    return result.returncode == 0