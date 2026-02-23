#!/usr/bin/env python3
"""
Verify that all import paths in routes files match the actual file structure.
Run from backend dir: python -m tests.verification.verify_imports
"""
import re
from pathlib import Path
from collections import defaultdict

# Backend root (tests/verification -> tests -> backend)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
backend_dir = BACKEND_DIR
src_dir = backend_dir / "src"

errors = []
warnings = []


def file_exists(file_path):
    return file_path.exists()


def check_import_statement(import_line, source_file):
    pattern = r'^from (src\.[a-z_\.]+) import'
    match = re.match(pattern, import_line.strip())
    if not match:
        return None

    import_path = match.group(1)
    file_path = backend_dir / f"{import_path.replace('.', '/')}.py"

    if file_exists(file_path):
        return f"✅ {import_line}"
    elif (backend_dir / import_path.replace('.', '/')).is_dir():
        init_file = backend_dir / f"{import_path.replace('.', '/')}/__init__.py"
        if file_exists(init_file):
            return f"✅ {import_line}"
        else:
            return f"❌ {import_line} -> Missing __init__.py in {import_path.replace('.', '/')}"
    else:
        return f"❌ {import_line} -> File/directory not found: {file_path}"


def main():
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

    for file_path in sorted(all_imports.keys()):
        relative_path = file_path.relative_to(src_dir)
        print(f"\n📄 {relative_path}")
        print("-" * 80)
        for line_num, import_line, result in all_imports[file_path]:
            print(f"  Line {line_num}: {result}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if errors:
        print(f"\n❌ Found {len(errors)} import path errors:\n")
        for error in errors:
            print(f"  {error}")
        return 1
    else:
        print("\n✅ All import paths are correctly configured!")
        print(f"   Checked {len(route_files)} route files")
        return 0


if __name__ == "__main__":
    exit(main())
