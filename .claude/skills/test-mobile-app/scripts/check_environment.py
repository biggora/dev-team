#!/usr/bin/env python3
"""
check_environment.py — Verify all dependencies for mobile testing are available.
"""
import subprocess
import sys
import json
import shutil

def check(label: str, fn) -> dict:
    try:
        result = fn()
        return {"label": label, "ok": True, "detail": result}
    except Exception as e:
        return {"label": label, "ok": False, "detail": str(e)}

def check_adb():
    if not shutil.which("adb"):
        raise RuntimeError("adb not found — install Android SDK Platform Tools")
    out = subprocess.run(["adb", "version"], capture_output=True, text=True)
    return out.stdout.strip().split("\n")[0]

def check_emulator():
    if not shutil.which("emulator"):
        raise RuntimeError("emulator binary not found — install Android SDK Emulator")
    out = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    devices = [l for l in out.stdout.strip().split("\n")[1:] if l.strip()]
    if not devices:
        raise RuntimeError("No devices/emulators connected. Run an emulator first.")
    return f"{len(devices)} device(s): {', '.join(d.split()[0] for d in devices)}"

def check_appium_server():
    import urllib.request
    try:
        resp = urllib.request.urlopen("http://localhost:4723/status", timeout=3)
        data = json.loads(resp.read())
        return f"Appium running — {data.get('value', {}).get('build', {}).get('version', 'unknown')}"
    except Exception:
        raise RuntimeError("Appium server not running. Start with: appium --base-path /wd/hub")

def check_appium_python():
    import appium
    return f"appium-python-client {appium.__version__}"

def check_python_deps():
    missing = []
    pkg_map = {"pytest": "pytest", "jinja2": "jinja2", "PIL": "pillow"}
    for import_name, install_name in pkg_map.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(install_name)
    if missing:
        raise RuntimeError(f"Missing packages: {missing}. Run: pip install {' '.join(missing)} --break-system-packages")
    return "All Python deps OK"

def check_avd():
    """List available Android Virtual Devices"""
    if not shutil.which("avdmanager"):
        raise RuntimeError("avdmanager not found — install Android SDK")
    out = subprocess.run(["avdmanager", "list", "avd"], capture_output=True, text=True)
    avds = [l.strip() for l in out.stdout.split("\n") if "Name:" in l]
    if not avds:
        raise RuntimeError("No AVDs configured. Create one with: avdmanager create avd -n test -k 'system-images;android-30;google_apis;x86_64'")
    return f"{len(avds)} AVD(s): {', '.join(a.replace('Name:', '').strip() for a in avds)}"

def main():
    checks = [
        ("ADB", check_adb),
        ("Android Virtual Devices", check_avd),
        ("Connected Device/Emulator", check_emulator),
        ("Appium Server", check_appium_server),
        ("Appium Python Client", check_appium_python),
        ("Python Dependencies", check_python_deps),
    ]

    print("\n🔍 MOBILE TESTING ENVIRONMENT CHECK")
    print("=" * 50)

    all_ok = True
    critical_missing = []

    for label, fn in checks:
        r = check(label, fn)
        icon = "✅" if r["ok"] else "❌"
        print(f"{icon}  {label}")
        if r["ok"]:
            print(f"      {r['detail']}")
        else:
            print(f"      ⚠️  {r['detail']}")
            all_ok = False
            if label in ("ADB", "Appium Python Client"):
                critical_missing.append(label)

    print("=" * 50)

    if all_ok:
        print("\n✅ All checks passed — ready for automated testing!")
    elif not critical_missing:
        print("\n⚠️  Some optional components missing — can run in STATIC mode.")
        print("    Use: python3 run_tests.py --static")
    else:
        print(f"\n❌ Critical missing: {critical_missing}")
        print("   Install missing tools and re-run.")
        print("\n📖 See references/setup-appium.md for setup instructions.")
        sys.exit(1)

    # Summary JSON for scripts
    return {
        "all_ok": all_ok,
        "critical_missing": critical_missing,
        "mode": "automated" if all_ok else "static"
    }

if __name__ == "__main__":
    main()