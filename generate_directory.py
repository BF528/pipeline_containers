#!/usr/bin/env python

"""
generate_directory.py - Scaffold per-tool container directories from env YMLs.

For each env YML found in the envs directory, creates a subdirectory under the
containers directory containing:
  - The env YML
  - A rendered Dockerfile from the template file
  - A conda-lock.yml lockfile for reproducible builds

Existing tool directories are skipped by default. Use --overwrite to regenerate
all, or --tools to target specific tools regardless of whether they already exist.

Usage:
    python generate_directory.py
    python generate_directory.py --overwrite
    python generate_directory.py --tools samtools biopython
    python generate_directory.py --envs-dir envs --containers-dir containers --template template.txt
"""

import argparse
import glob
import os
import shutil
import subprocess


def get_tool_name(env_path: str) -> str:
    """Extract the tool name from an env YML path.

    For example, envs/biopython_env.yml -> biopython
    """
    basename = os.path.basename(env_path)
    return basename.split("_")[0]


def render_dockerfile(tool_dir: str, env_filename: str, template_file: str) -> None:
    """Render the Dockerfile template into the tool directory."""
    dockerfile_path = os.path.join(tool_dir, "Dockerfile")

    with open(template_file, "rt") as template, open(dockerfile_path, "w") as dockerfile:
        for line in template:
            dockerfile.write(line.replace("<env_desc>", env_filename))


def generate_lockfile(tool_dir: str, env_path: str) -> None:
    """Generate a conda-lock lockfile for the given env YML."""
    subprocess.run(
        [
            "conda-lock", "lock",
            "--file", env_path,
            "--platform", "linux-64",
            "--micromamba",
            "--lockfile", os.path.join(tool_dir, "conda-lock.yml"),
        ],
        check=True,
    )


def scaffold_tool(env_path: str, containers_dir: str, template_file: str) -> None:
    """Scaffold a container directory for a single tool."""
    tool = get_tool_name(env_path)
    tool_dir = os.path.join(containers_dir, tool)
    env_filename = os.path.basename(env_path)
    dest_env_path = os.path.join(tool_dir, env_filename)

    os.makedirs(tool_dir, exist_ok=True)
    shutil.copyfile(env_path, dest_env_path)
    render_dockerfile(tool_dir, env_filename, template_file)
    generate_lockfile(tool_dir, dest_env_path)


def should_scaffold(tool: str, tool_dir: str, overwrite: bool, targets: list[str]) -> tuple[bool, str]:
    """Determine whether a tool should be scaffolded and why.

    Returns a (should_run, reason) tuple.
    """
    already_exists = os.path.isdir(tool_dir)

    if targets:
        if tool not in targets:
            return False, "not in --tools list, skipping"
        return True, "targeted via --tools"

    if already_exists and not overwrite:
        return False, "already exists, skipping (use --overwrite to regenerate)"

    if already_exists and overwrite:
        return True, "regenerating (--overwrite)"

    return True, "new"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold per-tool container directories from env YMLs."
    )
    parser.add_argument(
        "--envs-dir",
        default="envs",
        help="Directory containing env YML files (default: envs/)",
    )
    parser.add_argument(
        "--containers-dir",
        default="containers",
        help="Output directory for scaffolded tool directories (default: containers/)",
    )
    parser.add_argument(
        "--template",
        default="template.txt",
        help="Path to the Dockerfile template (default: template.txt)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate all tool directories, including existing ones",
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        metavar="TOOL",
        help="Only scaffold the specified tools, skipping all others",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    env_paths = glob.glob(os.path.join(args.envs_dir, "*_env.yml"))

    if not env_paths:
        print(f"No env YMLs found in {args.envs_dir}/")
        return

    for env_path in sorted(env_paths):
        tool = get_tool_name(env_path)
        tool_dir = os.path.join(args.containers_dir, tool)
        run, reason = should_scaffold(tool, tool_dir, args.overwrite, args.tools or [])

        if not run:
            print(f"  {tool}: {reason}")
            continue

        print(f"Scaffolding {tool} ({reason})...")
        scaffold_tool(env_path, args.containers_dir, args.template)
        print(f"  done -> {tool_dir}/")


if __name__ == "__main__":
    main()