#!/usr/bin/env python3
"""
Test script to verify all imports in the routes directory are correctly configured.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

errors = []
successes = []

def test_import(import_path, description):
    """Test if a given import path can be imported."""
    try:
        __import__(import_path)
        successes.append(f"✅ {description}")
        return True
    except Exception as e:
        errors.append(f"❌ {description}: {str(e)}")
        return False

# Test all route imports
print("Testing route imports...")
print("-" * 60)

# Test individual route modules
test_import("src.routes.auth", "routes/auth")
test_import("src.routes.profile", "routes/profile")
test_import("src.routes.health", "routes/health")
test_import("src.routes.medication", "routes/medication")
test_import("src.routes.meditation", "routes/meditation")
test_import("src.routes.appointments", "routes/appointments")
test_import("src.routes.emergency", "routes/emergency")
test_import("src.routes.chat", "routes/chat")
test_import("src.routes.voice", "routes/voice")
test_import("src.routes.alarms", "routes/alarms")

# Test schema imports
print("\nTesting schema imports...")
print("-" * 60)

test_import("src.schemas", "schemas/__init__")
test_import("src.schemas.auth", "schemas/auth")
test_import("src.schemas.profile", "schemas/profile")
test_import("src.schemas.health", "schemas/health")
test_import("src.schemas.medication", "schemas/medication")
test_import("src.schemas.meditation", "schemas/meditation")
test_import("src.schemas.appointments", "schemas/appointments")
test_import("src.schemas.emergency", "schemas/emergency")
test_import("src.schemas.events", "schemas/events")

# Test main imports
print("\nTesting main application...")
print("-" * 60)

test_import("src.config", "config")
test_import("src.auth.dependencies", "auth/dependencies")
test_import("src.services.locusgraph.service", "services/locusgraph/service")

# Print results
print("\n" + "=" * 60)
print(f"✅ Successes: {len(successes)}")
print(f"❌ Errors: {len(errors)}")

if errors:
    print("\nErrors:")
    for error in errors:
        print(f"  {error}")
    sys.exit(1)
else:
    print("\n✅ All imports are correctly configured!")
    sys.exit(0)
