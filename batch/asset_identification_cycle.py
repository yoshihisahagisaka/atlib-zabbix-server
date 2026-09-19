"""InfraVision automatic asset-identification cycle.

Designed for a periodic job. The first production deployment should run without
--apply and review the JSON/console output. Once validated, schedule --apply.

Order:
1. resolve accumulated host SNMP evidence
2. link only uniquely resolved templates
3. leave ambiguous/unknown devices untouched

This job intentionally does not perform EoL/CVE decisions; those remain in the
security intelligence batch after inventory enrichment has had time to collect.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--host-group", default="")
    args = p.parse_args()

    cmd = [sys.executable, str(HERE / "apply_family_templates.py")]
    if args.apply:
        cmd.append("--apply")
    if args.host_group:
        cmd += ["--host-group", args.host_group]

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[InfraVision Asset Cycle] mode={mode}")
    result = subprocess.run(cmd, check=False)
    if result.returncode:
        print(f"[ERROR] family/template resolver failed: rc={result.returncode}")
        return result.returncode

    print("[OK] family/template resolution completed")
    print("[NEXT] inventory enrichment is collected by linked templates; EoL/CVE batch runs separately.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
