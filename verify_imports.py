#!/usr/bin/env python3
"""
Verify that all import paths in routes files match the actual file structure.
"""
import re
from pathlib import Path
from collections import defaultdict

backend_dir = Path("/media/merklenode/Buildbox/bro/podd/backend")
src_dir = backend_dir / "src"

errors = []
warnings = []

def file_exists(file_path):
    """Check if a file exists."""
    return file_path.exists()

def check_import_statement(import_line, source_file):
    """Check if an import statement is correct."""
    # Match patterns like:
    # from src.schemas.health import ...
    # from src.schemas.events import EventKind
    # from src.schemas.medication import (...)
    pattern = r'^from (src\.[a-z_\.]+) import'

    match = re.match(pattern, import_line.strip())
    if not match:
        return None

    import_path = match.group(1)
    # Remove the 'src.' prefix since we're already in the src directory
    module_path = import_path.replace('src.', '')
    file_path = backend_dir / f"{import_path.replace('.', '/')}.py"

    if file_exists(file_path):
        return f"✅ {import_line}"
    elif (backend_dir / import_path.replace('.', '/')).is_dir():
        # Check if __init__.py exists
        init_file = backend_dir / f"{import_path.replace('.', '/')}/__init__.py"
        if file_exists(init_file):
            return f"✅ {import_line}"
        else:
            return f"❌ {import_line} -> Missing __init__.py in {import_path.replace('.', '/')}"
    else:
        return f"❌ {import_line} -> File/directory not found: {file_path}"

# Scan all Python files in routes directory
routes_dir = src_dir / "routes"
route_files = list(routes_dir.rglob("*.py"))

print("Scanning route files for import statements...")
print("=" * 80)

all_imports = defaultdict(list)

for route_file in route_files:
    if route_file.name == "__init__.py":
        continue

    relative_path = route_file.relative_to(src_dir)
    with open(route_file, 'r') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        if line.startswith('from src.'):
            result = check_import_statement(line, route_file)
            if result:
                all_imports[route_file].append((line_num, line.strip(), result))
                if "❌" in result:
                    errors.append(f"{relative_path}:{line_num} - {result}")

# Print all imports
for file_path in sorted(all_imports.keys()):
    relative_path = file_path.relative_to(src_dir)
    print(f"\n📄 {relative_path}")
    print("-" * 80)
    for line_num, import_line, result in all_imports[file_path]:
        print(f"  Line {line_num}: {result}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if errors:
    print(f"\n❌ Found {len(errors)} import path errors:\n")
    for error in errors:
        print(f"  {error}")
    exit(1)
else:
    print("\n✅ All import paths are correctly configured!")
    print(f"   Checked {len(route_files)} route files")
    print(f"   Verified all 'from src.' import statements")

# Additional checks
print("\n" + "=" * 80)
print("ADDITIONAL CHECKS")
print("=" * 80)

# Check that all __init__.py files exist
print("\nChecking __init__.py files...")
missing_init = []

for schema_dir in (src_dir / "schemas").iterdir():
    if schema_dir.is_dir() and not schema_dir.name.startswith('_'):
        init_file = schema_dir / "__init__.py"
        if not init_file.exists():
            missing_init.append(str(schema_dir.relative_to(src_dir)))

if missing_init:
    print("❌ Missing __init__.py files:")
    for missing in missing_init:
        print(f"  {missing}")
else:
    print("✅ All schema directories have __init__.py")

# Check routes __init__.py files
print("\nChecking routes __init__.py files...")
missing_init = []

for route_dir in (src_dir / "routes").iterdir():
    if route_dir.is_dir() and not route_dir.name.startswith('_'):
        init_file = route_dir / "__init__.py"
        if not init_file.exists():
            missing_init.append(str(route_dir.relative_to(src_dir)))

if missing_init:
    print("❌ Missing __init__.py files:")
    for missing in missing_init:
        print(f"  {missing}")
else:
    print("✅ All route directories have __init__.py")

print("\n" + "=" * 80)

if not errors and not missing_init:
    print("✅ ALL CHECKS PASSED - Import paths are correctly configured!")
    exit(0)
else:
    print("⚠️  Some issues found - please review above")
    exit(1)
