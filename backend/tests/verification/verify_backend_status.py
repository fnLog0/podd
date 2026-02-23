#!/usr/bin/env python3
"""
Verify BACKEND_TODO.md status matches actual implementation.
Run from backend dir: python -m tests.verification.verify_backend_status
"""
import re
from pathlib import Path

# Backend root (tests/verification -> tests -> backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROUTES_DIR = BASE_DIR / "src" / "routes"

# Expected endpoints from BACKEND_TODO.md
EXPECTED_ENDPOINTS = {
    "auth": [
        ("POST", "/api/auth/register"),
        ("POST", "/api/auth/login"),
        ("POST", "/api/auth/logout"),
        ("POST", "/api/auth/refresh"),
        ("GET", "/api/auth/me"),
    ],
    "chat": [
        ("POST", "/api/chat"),
        ("GET", "/api/chat/history"),
    ],
    "voice": [
        ("POST", "/api/voice/stream"),
        ("POST", "/api/voice/synthesize"),
        ("POST", "/api/voice/conversation"),
        ("WS", "/ws/voice"),
    ],
    "profile": [
        ("GET", "/api/profile"),
        ("PUT", "/api/profile"),
    ],
    "health": [
        ("POST", "/api/health/vitals"),
        ("GET", "/api/health/vitals"),
        ("GET", "/api/health/insights"),
        ("GET", "/api/health/recommendations"),
        ("POST", "/api/health/food/log"),
        ("GET", "/api/health/food/logs"),
    ],
    "medication": [
        ("POST", "/api/medication/log"),
        ("GET", "/api/medication/schedule"),
        ("POST", "/api/medication/schedule"),
    ],
    "water": [
        ("POST", "/api/water/log"),
        ("GET", "/api/water/history"),
    ],
    "sleep": [
        ("POST", "/api/sleep/log"),
        ("GET", "/api/sleep/history"),
    ],
    "exercise": [
        ("POST", "/api/exercise/log"),
        ("GET", "/api/exercise/history"),
    ],
    "mood": [
        ("POST", "/api/mood/log"),
        ("GET", "/api/mood/history"),
    ],
    "meditation": [
        ("GET", "/api/meditation/sessions"),
        ("GET", "/api/meditation/sessions/{id}"),
        ("POST", "/api/meditation/log"),
        ("GET", "/api/meditation/history"),
    ],
    "alarms": [
        ("POST", "/api/alarms"),
        ("GET", "/api/alarms"),
        ("PUT", "/api/alarms/{id}"),
        ("DELETE", "/api/alarms/{id}"),
    ],
    "appointments": [
        ("POST", "/api/appointments"),
        ("GET", "/api/appointments"),
        ("PUT", "/api/appointments/{id}"),
    ],
    "notifications": [
        ("GET", "/api/notifications"),
        ("PUT", "/api/notifications/{id}/read"),
    ],
    "emergency_contacts": [
        ("POST", "/api/emergency-contacts"),
        ("GET", "/api/emergency-contacts"),
    ],
}

STUB_PATTERN = re.compile(r'["\']not implemented["\']|raise NotImplementedError|TODO|FIXME|NotImplementedError')


def check_endpoint_implemented(category, method, path):
    category_map = {
        "auth": "auth",
        "chat": "chat",
        "voice": "voice",
        "profile": "profile",
        "health": "health/health",
        "medication": "medication",
        "water": "health",
        "sleep": "health",
        "exercise": "health",
        "mood": "health",
        "meditation": "meditation",
        "alarms": "alarms/alarms",
        "appointments": "appointments",
        "notifications": "alarms/notifications",
        "emergency_contacts": "emergency",
    }
    route_file = category_map.get(category, category)
    route_path = ROUTES_DIR / f"{route_file}.py"

    if not route_path.exists():
        return False, f"File not found: {route_path}"

    with open(route_path, 'r') as f:
        content = f.read()

    endpoint_pattern = re.compile(
        rf'@router\.{method.lower()}\(["\']{re.escape(path)}["\']',
        re.MULTILINE
    )
    match = endpoint_pattern.search(content)
    if not match:
        return False, "Endpoint definition not found"

    start_pos = match.end()
    next_decorator = re.search(r'\n@router\.', content[start_pos:])
    next_function = re.search(r'\ndef ', content[start_pos:])
    if next_decorator and next_function:
        next_pos = min(next_decorator.start(), next_function.start())
    elif next_decorator:
        next_pos = next_decorator.start()
    elif next_function:
        next_pos = next_function.start()
    else:
        next_pos = len(content[start_pos:])
    function_body = content[start_pos:start_pos + next_pos]

    if STUB_PATTERN.search(function_body):
        return False, "Contains 'not implemented' or similar stub"

    non_comment_lines = [
        line for line in function_body.split('\n')
        if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""') and not line.strip().startswith("'''")
    ]
    if len(non_comment_lines) < 3:
        return False, "Function body too short (likely stub)"

    return True, "Implemented"


def main():
    print("=" * 70)
    print("BACKEND TODO STATUS VERIFICATION")
    print("=" * 70)
    print()

    total_expected = 0
    total_implemented = 0
    total_stubs = 0
    total_not_found = 0
    results_by_category = {}

    for category, endpoints in EXPECTED_ENDPOINTS.items():
        print(f"\n{'─' * 70}")
        print(f"{category.upper().replace('_', ' ')}")
        print(f"{'─' * 70}")
        category_implemented = 0
        category_stubs = 0
        category_not_found = 0

        for method, path in endpoints:
            total_expected += 1
            implemented, reason = check_endpoint_implemented(category, method, path)
            if implemented:
                status = "✅ IMPLEMENTED"
                category_implemented += 1
                total_implemented += 1
            elif "not implemented" in reason.lower() or "stub" in reason.lower():
                status = "❌ STUB"
                category_stubs += 1
                total_stubs += 1
            else:
                status = f"❌ NOT FOUND ({reason})"
                category_not_found += 1
                total_not_found += 1
            print(f"  {status:<20} {method:<6} {path}")

        results_by_category[category] = {
            "total": len(endpoints),
            "implemented": category_implemented,
            "stubs": category_stubs,
            "not_found": category_not_found,
        }

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nTotal Endpoints: {total_expected}")
    print(f"✅ Implemented:   {total_implemented} ({100*total_implemented//total_expected}%)")
    print(f"❌ Stubs:         {total_stubs} ({100*total_stubs//total_expected if total_expected else 0}%)")
    print(f"❌ Not Found:     {total_not_found} ({100*total_not_found//total_expected if total_expected else 0}%)")

    print("\n" + "=" * 70)
    print("STATUS BY PHASE")
    print("=" * 70)
    phase_1 = results_by_category.get("auth", {})
    phase_2 = {
        "total": sum(results_by_category[k]["total"] for k in ["profile", "health", "medication"]),
        "implemented": sum(results_by_category[k]["implemented"] for k in ["profile", "health", "medication"]),
        "stubs": sum(results_by_category[k]["stubs"] for k in ["profile", "health", "medication"]),
    }
    phase_3 = {
        "total": sum(results_by_category[k]["total"] for k in ["water", "sleep", "exercise", "mood"]),
        "implemented": sum(results_by_category[k]["implemented"] for k in ["water", "sleep", "exercise", "mood"]),
        "stubs": sum(results_by_category[k]["stubs"] for k in ["water", "sleep", "exercise", "mood"]),
    }
    phase_4 = {
        "total": sum(results_by_category[k]["total"] for k in ["meditation", "appointments", "emergency_contacts"]),
        "implemented": sum(results_by_category[k]["implemented"] for k in ["meditation", "appointments", "emergency_contacts"]),
        "stubs": sum(results_by_category[k]["stubs"] for k in ["meditation", "appointments", "emergency_contacts"]),
    }
    phase_5 = {
        "total": sum(results_by_category[k]["total"] for k in ["alarms", "notifications"]),
        "implemented": sum(results_by_category[k]["implemented"] for k in ["alarms", "notifications"]),
        "stubs": sum(results_by_category[k]["stubs"] for k in ["alarms", "notifications"]),
    }
    phase_6 = results_by_category.get("chat", {})
    phase_7 = results_by_category.get("voice", {})

    phases = [
        ("Phase 1: Auth", phase_1),
        ("Phase 2: Health & Core Tracking", phase_2),
        ("Phase 3: Additional Tracking", phase_3),
        ("Phase 4: Meditation & Appointments", phase_4),
        ("Phase 5: Alarms & Notifications", phase_5),
        ("Phase 6: LangGraph Workflow", phase_6),
        ("Phase 7: Voice Pipeline", phase_7),
    ]
    for phase_name, data in phases:
        total = data.get("total", 0)
        implemented = data.get("implemented", 0)
        stubs = data.get("stubs", 0)
        if total == 0:
            status, completion = "❌ NOT STARTED", "0%"
        elif stubs > 0:
            status, completion = "⚠️ PARTIAL (STUBS)", f"{100*implemented//total}%"
        elif implemented == total:
            status, completion = "✅ COMPLETE", "100%"
        else:
            status, completion = "⚠️ PARTIAL", f"{100*implemented//total}%"
        print(f"{status:<20} {phase_name:<35} {implemented}/{total} ({completion})")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
