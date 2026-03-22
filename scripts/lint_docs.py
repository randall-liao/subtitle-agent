import re
import sys
from pathlib import Path


def lint_markdown_links(file_path: Path):
    content = file_path.read_text()
    # Matches [Text](path/to/file)
    links = re.findall(r"\[.*?\]\((.*?)\)", content)

    errors = 0
    repo_root = Path(__file__).parent.parent

    for link in links:
        # Ignore external links, mailto, and anchors
        if (
            link.startswith("http")
            or link.startswith("#")
            or link.startswith("mailto:")
        ):
            continue

        # Strip anchors from internal links
        link_path = link.split("#")[0]
        if not link_path:
            continue

        # In github markdown, paths in README.md or AGENTS.md are usually relative to the file.
        target_path = (file_path.parent / link_path).resolve()

        if not target_path.exists():
            print(
                f"❌ Broken link in {file_path.relative_to(repo_root)}: '{link_path}' (resolved to {target_path})"
            )
            errors += 1

    return errors


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    agents_md = repo_root / "AGENTS.md"

    total_errors = 0
    if agents_md.exists():
        total_errors += lint_markdown_links(agents_md)

    for md_file in repo_root.glob("docs/**/*.md"):
        total_errors += lint_markdown_links(md_file)

    if total_errors > 0:
        print(f"\nFailed: Found {total_errors} broken cross-links in documentation.")
        sys.exit(1)

    print("✅ All internal markdown links are valid!")
    sys.exit(0)
