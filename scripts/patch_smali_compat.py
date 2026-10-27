"""Redirect TelephonyManager.getNetworkType() call sites in the apktool tree to cube.mod.Compat.

Idempotent.  usage: python -I patch_smali_compat.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "apktool_cube" / "smali"
CALL = re.compile(r"invoke-virtual \{(\w+)\}, Landroid/telephony/TelephonyManager;->getNetworkType\(\)I")
NEW = r"invoke-static {\1}, Lcube/mod/Compat;->networkType(Landroid/telephony/TelephonyManager;)I"

for path in ROOT.rglob("*.smali"):
    if path.parts[-3:-1] == ("cube", "mod"):
        continue
    text = path.read_text(encoding="utf-8")
    new, n = CALL.subn(NEW, text)
    if n:
        path.write_text(new, encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: {n}")
