#!/usr/bin/env python

"""
generate_envs.py - Generate conda env YMLs from a newline-separated list of packages.

Usage:
    python generate_envs.py <packages.txt>

Each line in the txt file should be a single package name. Empty lines and
lines beginning with '#' are ignored. One YML is created per package in the
envs/ directory following the convention: envs/<package>_env.yml.
"""

import argparse
import os
import sys


TEMPLATE = """\
channels:
  - conda-forge
  - bioconda

dependencies:
  - {package}
"""


def parse_packages(filepath: str) -> list[str]:
    packages = []
    with open(filepath, 'rt') as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                packages.append(stripped)
    return packages


def generate_yml(package: str, outdir: str) -> str:
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"{package}_env.yml")

    if os.path.exists(outpath):
        print(f"  skipping {outpath} (already exists)")
        return outpath

    with open(outpath, 'w') as f:
        f.write(TEMPLATE.format(package=package))

    print(f"  created {outpath}")
    return outpath


def main():
    parser = argparse.ArgumentParser(
        description="Generate conda env YMLs from a list of package names."
    )
    parser.add_argument(
        'packages_file',
        help='Path to newline-separated txt file of package names'
    )
    parser.add_argument(
        '--outdir',
        default='envs',
        help='Output directory for generated YMLs (default: envs/)'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing YML files'
    )
    args = parser.parse_args()

    if not os.path.exists(args.packages_file):
        print(f"Error: file not found: {args.packages_file}", file=sys.stderr)
        sys.exit(1)

    packages = parse_packages(args.packages_file)

    if not packages:
        print("No packages found in input file.", file=sys.stderr)
        sys.exit(1)

    print(f"Generating {len(packages)} env YML(s) in {args.outdir}/\n")

    for package in packages:
        if args.overwrite:
            outpath = os.path.join(args.outdir, f"{package}_env.yml")
            if os.path.exists(outpath):
                os.remove(outpath)
        generate_yml(package, args.outdir)

    print(f"\nDone. Run generate_directory.py to create tool directories and lockfiles.")


if __name__ == '__main__':
    main()