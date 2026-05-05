# zone2_5_zkml.py
# 🔥 WINDOWS → WSL SAFE VERSION
# FIX: 不要用 \ 多行，改單行字串

from wsl_ezkl_runner import run_ezkl


class ZKMLVerifier:

    def run(self):

        print("🔐 WSL EZKL VERIFY (AUTO VENV MODE)")

        # ✅ 單行 command（最穩）
        cmd = (
            "ezkl verify "
            "--proof-path proof.json "
            "--vk-path vk.key "
            "--settings-path settings.json"
        )

        ok = run_ezkl(cmd)

        if ok:
            print("✔ ZKML VERIFIED")
        else:
            print("❌ ZKML FAILED")

        return ok