#!/usr/bin/env python

"""
get_versions.py - Extract the primary tool version from each conda-lock lockfile.

For each lockfile found under the containers directory, reads the resolved version
of the tool package (inferred from the directory name) and prints a summary table.
Optionally inserts or updates the table at the top of the README.

Usage:
    python get_versions.py
    python get_versions.py --update-readme
    python get_versions.py --containers-dir containers --readme README.md
    python get_versions.py --tools samtools biopython
"""

import argparse
import glob
import os
import re
import yaml


README_TABLE_START = "<!-- versions-table-start -->"
README_TABLE_END = "<!-- versions-table-end -->"


def get_tool_name(tool_dir: str) -> str:
    """Extract the tool name from a containers subdirectory path.

    For example, containers/biopython -> biopython
    """
    return os.path.basename(tool_dir)


def get_tool_version(lockfile_path: str, tool_name: str) -> str | None:
    """Parse the conda-lock lockfile and return the resolved version of the tool.

    Returns None if the package is not found in the lockfile.
    """
    with open(lockfile_path, "rt") as f:
        lockfile = yaml.safe_load(f)

    packages = lockfile.get("package", [])

    for package in packages:
        if package.get("name") == tool_name:
            return package.get("version")

    return None


def build_markdown_table(results: dict[str, str]) -> str:
    """Render the version results as a markdown table."""
    lines = [
        "## Available Tools\n",
        "| Tool | Version |",
        "| ---- | ------- |",
    ]
    for tool, version in sorted(results.items()):
        lines.append(f"| `{tool}` | {version} |")
    return "\n".join(lines)


def update_readme(readme_path: str, table: str) -> None:
    """Insert or replace the version table in the README.

    The table is wrapped in HTML comments used as stable markers so it can
    be safely replaced on subsequent runs without affecting surrounding content.
    """
    with open(readme_path, "rt") as f:
        content = f.read()

    block = f"{README_TABLE_START}\n{table}\n{README_TABLE_END}"

    if README_TABLE_START in content:
        content = re.sub(
            rf"{re.escape(README_TABLE_START)}.*?{re.escape(README_TABLE_END)}",
            block,
            content,
            flags=re.DOTALL,
        )
    else:
        # Insert after the top-level heading
        content = re.sub(
            r"(^# .+\n)",
            rf"\1\n{block}\n",
            content,
            count=1,
            flags=re.MULTILINE,
        )

    with open(readme_path, "wt") as f:
        f.write(content)

    print(f"  updated {readme_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract primary tool versions from conda-lock lockfiles."
    )
    parser.add_argument(
        "--containers-dir",
        default="containers",
        help="Directory containing per-tool subdirectories (default: containers/)",
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        metavar="TOOL",
        help="Only report versions for the specified tools",
    )
    parser.add_argument(
        "--update-readme",
        action="store_true",
        help="Insert or update the version table in the README",
    )
    parser.add_argument(
        "--readme",
        default="README.md",
        help="Path to the README file to update (default: README.md)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    lockfile_paths = glob.glob(
        os.path.join(args.containers_dir, "*", "conda-lock.yml")
    )

    if not lockfile_paths:
        print(f"No lockfiles found under {args.containers_dir}/")
        return

    results = {}

    for lockfile_path in sorted(lockfile_paths):
        tool_dir = os.path.dirname(lockfile_path)
        tool = get_tool_name(tool_dir)

        if args.tools and tool not in args.tools:
            continue

        version = get_tool_version(lockfile_path, tool)
        results[tool] = version if version else "not found in lockfile"

    col_width = max(len(t) for t in results) + 2
    print(f"\n{'Tool':<{col_width}} Version")
    print("-" * (col_width + 16))
    for tool, version in sorted(results.items()):
        print(f"{tool:<{col_width}} {version}")
    print()

    if args.update_readme:
        if not os.path.exists(args.readme):
            print(f"README not found: {args.readme}")
            return
        table = build_markdown_table(results)
        update_readme(args.readme, table)


if __name__ == "__main__":
    main()