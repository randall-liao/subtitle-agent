import ast
import sys
from pathlib import Path

RULES = {
    "cli": {"allowed_internal_imports": []},
    "core": {"allowed_internal_imports": []},
    "agent": {"allowed_internal_imports": ["core", "cli"]},
    "main": {"allowed_internal_imports": ["core", "cli", "agent"]},
}


def get_imports(file_path: Path):
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_base = node.module.split(".")[0]
                if node.level == 0:
                    imports.append(module_base)
                else:
                    # relative import, assume it's same level for simplicity
                    parent_dir = file_path.parent.name
                    if node.level == 1:
                        imports.append(parent_dir)
                    elif node.level == 2:
                        imports.append(file_path.parent.parent.name)
            else:
                pass
    return imports


def lint_architecture():
    repo_root = Path(__file__).parent.parent
    src_dir = repo_root / "src"

    errors = 0

    for python_file in src_dir.rglob("*.py"):
        rel_path = python_file.relative_to(src_dir)
        module_name = rel_path.parts[0]

        if module_name == "main.py":
            module_name = "main"

        if module_name not in RULES:
            continue

        allowed = RULES[module_name]["allowed_internal_imports"]
        imports = get_imports(python_file)

        for imp in imports:
            if imp in RULES and imp != module_name and imp not in allowed:
                print(f"❌ ARCHITECTURE VIOLATION in {rel_path}:")
                print(
                    f"   Module '{module_name}' is not allowed to import from internal module '{imp}'."
                )
                print(f"   Allowed internal imports: {allowed}")
                errors += 1

    if errors > 0:
        print(f"\nFailed: Found {errors} architectural layer violations.")
        sys.exit(1)

    print("✅ Architecture constraints validated perfectly!")
    sys.exit(0)


if __name__ == "__main__":
    lint_architecture()
