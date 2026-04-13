#!/usr/bin/env python3
"""
analyze_apk.py — Extract structure from Android APK for use case generation.
Usage: python3 analyze_apk.py path/to/app.apk [--json]
"""
import sys
import json
import argparse

def analyze_apk(apk_path: str) -> dict:
    result = {
        "package": None,
        "version": None,
        "activities": [],
        "permissions": [],
        "services": [],
        "receivers": [],
        "providers": [],
        "strings_sample": [],
        "min_sdk": None,
        "target_sdk": None,
    }

    try:
        from androguard.core.bytecodes.apk import APK
        apk = APK(apk_path)

        result["package"] = apk.get_package()
        result["version"] = apk.get_androidversion_name()
        result["min_sdk"] = apk.get_min_sdk_version()
        result["target_sdk"] = apk.get_target_sdk_version()

        # Activities
        for act in apk.get_activities():
            is_main = act == apk.get_main_activity()
            result["activities"].append({
                "name": act.split(".")[-1],
                "full_name": act,
                "is_main": is_main
            })

        # Permissions
        result["permissions"] = list(apk.get_permissions())

        # Services
        result["services"] = [s.split(".")[-1] for s in apk.get_services()]

        # Broadcast receivers
        result["receivers"] = [r.split(".")[-1] for r in apk.get_receivers()]

        # String resources (sample)
        try:
            # Try modern androguard API first, fall back to legacy
            try:
                from androguard.core.axml import AXMLPrinter
                res_parser = apk.get_android_resources()
                if res_parser:
                    strings = res_parser.get_resolved_strings()
                    if strings:
                        for lang_strings in strings.values():
                            result["strings_sample"] = list(lang_strings.values())[:30]
                            break
            except (ImportError, AttributeError):
                # Fallback: extract string-like values from manifest
                manifest_xml = apk.get_android_manifest_xml()
                if manifest_xml is not None:
                    result["strings_sample"] = []
        except Exception:
            pass

    except ImportError:
        result["error"] = "androguard not installed. Run: pip install androguard --break-system-packages"
    except Exception as e:
        result["error"] = str(e)

    return result


def print_human_readable(data: dict):
    print(f"\n{'='*60}")
    print(f"  APK ANALYSIS REPORT")
    print(f"{'='*60}")
    print(f"Package:     {data.get('package', 'unknown')}")
    print(f"Version:     {data.get('version', 'unknown')}")
    print(f"Min SDK:     {data.get('min_sdk', '?')}  |  Target SDK: {data.get('target_sdk', '?')}")

    activities = data.get("activities", [])
    print(f"\n📱 SCREENS / ACTIVITIES ({len(activities)}):")
    for act in activities:
        marker = " ← MAIN" if act.get("is_main") else ""
        print(f"  • {act['name']}{marker}")

    permissions = data.get("permissions", [])
    if permissions:
        print(f"\n🔒 PERMISSIONS ({len(permissions)}):")
        for p in permissions:
            short = p.replace("android.permission.", "")
            print(f"  • {short}")

    services = data.get("services", [])
    if services:
        print(f"\n⚙️  SERVICES: {', '.join(services)}")

    strings = data.get("strings_sample", [])
    if strings:
        print(f"\n📝 STRING KEYS (sample): {', '.join(strings[:15])}")

    if "error" in data:
        print(f"\n⚠️  Error: {data['error']}")

    print(f"\n{'='*60}")

    # Inferred features
    print("\n💡 INFERRED FEATURES (for use case generation):")
    perms = " ".join(data.get("permissions", []))
    acts = [a["name"].lower() for a in activities]

    hints = []
    if "CAMERA" in perms: hints.append("📷 Camera / photo capture")
    if "READ_CONTACTS" in perms or "WRITE_CONTACTS" in perms: hints.append("👥 Contacts access")
    if "INTERNET" in perms: hints.append("🌐 Network/API calls")
    if "ACCESS_FINE_LOCATION" in perms or "ACCESS_COARSE_LOCATION" in perms: hints.append("📍 Location/maps")
    if "READ_EXTERNAL_STORAGE" in perms or "WRITE_EXTERNAL_STORAGE" in perms: hints.append("💾 File storage")
    if "RECORD_AUDIO" in perms: hints.append("🎙️ Audio recording")
    if "SEND_SMS" in perms or "RECEIVE_SMS" in perms: hints.append("💬 SMS")
    if "VIBRATE" in perms: hints.append("📳 Notifications")
    if "USE_BIOMETRIC" in perms or "USE_FINGERPRINT" in perms: hints.append("🔐 Biometric auth")

    for act_name in acts:
        if "login" in act_name or "auth" in act_name or "sign" in act_name:
            hints.append("🔑 Authentication screen detected")
        if "register" in act_name or "signup" in act_name:
            hints.append("📝 Registration screen detected")
        if "main" in act_name or "home" in act_name or "dashboard" in act_name:
            hints.append("🏠 Main/Dashboard screen")
        if "settings" in act_name or "profile" in act_name:
            hints.append("⚙️ Settings/Profile screen")
        if "payment" in act_name or "checkout" in act_name:
            hints.append("💳 Payment/Checkout flow")
        if "map" in act_name or "location" in act_name:
            hints.append("🗺️ Map screen")
        if "list" in act_name or "feed" in act_name:
            hints.append("📋 List/Feed screen")
        if "detail" in act_name:
            hints.append("🔍 Detail view")
        if "search" in act_name:
            hints.append("🔍 Search functionality")
        if "chat" in act_name or "message" in act_name:
            hints.append("💬 Messaging/Chat")
        if "notification" in act_name:
            hints.append("🔔 Notification screen")

    # Deduplicate
    seen = set()
    for h in hints:
        if h not in seen:
            print(f"  {h}")
            seen.add(h)

    if not hints:
        print("  (Could not infer specific features — generate use cases from activity names)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze APK for mobile testing")
    parser.add_argument("apk", help="Path to APK file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    data = analyze_apk(args.apk)

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_human_readable(data)