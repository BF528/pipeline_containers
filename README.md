# Monorepo for Docker containers used in BF528 - Applications in Translational Bioinformatics

![Build](https://github.com/bf528/pipeline_containers/actions/workflows/build.yml/badge.svg?branch=main)
![Update Lockfiles](https://github.com/bf528/pipeline_containers/actions/workflows/update_lockfiles.yml/badge.svg?branch=main)


<!-- versions-table-start -->
## Available Tools

| Tool | Version |
| ---- | ------- |
| `bedtools` | 2.31.1 |
| `biopython` | 1.86 |
| `bowtie2` | 2.5.5 |
| `deeptools` | 3.5.6 |
| `fastqc` | 0.12.1 |
| `homer` | 5.1 |
| `jbrowse2` | 4.1.3 |
| `kmer-jellyfish` | 2.3.1 |
| `macs3` | 3.0.4 |
| `multiqc` | 1.33 |
| `ncbi-datasets-cli` | 18.20.0 |
| `pandas` | 3.0.1 |
| `prokka` | 1.15.6 |
| `pysam` | 0.23.3 |
| `samtools` | 1.23 |
| `star` | 2.7.11b |
| `subread` | 2.1.1 |
| `trimmomatic` | 0.40 |
| `verse` | 0.1.5 |
<!-- versions-table-end -->

## Overview

This repo contains all of the containers and their specifications required for use in BF528.
Each container is built from a templated Dockerfile using a conda environment specification.
Only tools and packages installable via micromamba are used. Reproducibility is enforced via
`conda-lock` lockfiles committed alongside each environment specification.

Images are published to the GitHub Container Registry (GHCR) and can be pulled directly:

```bash
docker pull ghcr.io/bf528/<tool>:latest
```

---

## Repository Structure

```
.
├── containers/                  # Generated per-tool directories (do not edit manually)
│   └── <tool>/
│       ├── <tool>_env.yml
│       ├── conda-lock.yml       # Fully resolved lockfile for reproducible builds
│       └── Dockerfile
├── envs/                        # Source environment specifications (one per tool)
│   ├── <tool>_env.yml
│   └── repo_requirements.yml    # Local dev dependencies
├── template.txt                 # Dockerfile template used by generate_directory.py
├── packages.txt                 # Canonical list of all tools in the repo
├── generate_envs.py             # Generates env YMLs from packages.txt
└── generate_directory.py        # Scaffolds per-tool directories from envs/
```

---

## Requirements

- The repository must be **public** (GHCR packages inherit repo visibility)
- `conda-lock` must be installed locally to run the setup scripts. A `repo_requirements.yml`
  is provided in `envs/` for this purpose:

```bash
mamba install -f envs/repo_requirements.yml
```

---

## Implementation Checklist

### CI/CD
- [x] Build and publish workflow (`build.yml`) using `git diff` — no third-party actions
- [x] Changed directory detection scoped to `containers/` only
- [x] Dual image tagging (`:latest` and `:<sha>`)
- [x] Annual lockfile update workflow (`update_lockfiles.yml`) triggering on August 1st
- [x] Manual `workflow_dispatch` trigger with optional single-tool input
- [x] Per-tool error handling in lockfile updates — partial failures still open a PR
- [x] Conda package caching in lockfile update workflow
- [x] Lockfile update PRs include success/failure summary in PR body

### Reproducibility
- [x] `conda-lock` lockfiles committed per tool
- [x] Dockerfiles install from lockfile (`--freeze-installed`) rather than resolving at build time
- [x] Unpinned `env.yml` specifications — intent separated from exact versions

### Developer Experience
- [x] `packages.txt` as canonical source of truth for all tools
- [x] `generate_envs.py` to scaffold env YMLs from `packages.txt`
- [x] `generate_directory.py` generates tool directories, Dockerfiles, and lockfiles
- [x] `generate_directory.py` skips existing tools by default, supports `--overwrite` and `--tools`
- [x] `get_versions.py` extracts resolved tool versions from lockfiles and optionally updates the README
- [x] `repo_requirements.yml` for local dev environment setup

---

## Adding a New Tool

**1. Add the package name to `packages.txt`:**

```
samtools
biopython
<new-tool>
```

The package name must match the exact conda package name as it appears on `conda-forge`
or `bioconda`. The env YML filename will be derived from this name.

**2. Generate the env YML:**

```bash
python generate_envs.py packages.txt
```

This creates `envs/<tool>_env.yml`. Existing YMLs are skipped by default. Pass `--overwrite`
to regenerate all. Use `--outdir` to specify a custom output directory.

**3. Scaffold the tool directory and generate the lockfile:**

```bash
python generate_directory.py
```

This creates `containers/<tool>/`, copies the env YML, renders the Dockerfile from
`template.txt`, and generates a `conda-lock.yml` for reproducible builds. Existing
tool directories are skipped by default — only new tools are scaffolded.

To regenerate all tools:

```bash
python generate_directory.py --overwrite
```

To regenerate specific tools only:

```bash
python generate_directory.py --tools samtools biopython
```

All other flags and their defaults:

```
--envs-dir      Directory containing env YMLs       (default: envs/)
--containers-dir  Output directory for tool dirs     (default: containers/)
--template      Path to the Dockerfile template      (default: template.txt)
```

**4. Commit and push:**

```
feat: add <tool> container
```

The CI pipeline will detect the new directory under `containers/` and automatically
build and push the image.

---

## Environment Specifications

Each `envs/<tool>_env.yml` specifies the tool and conda channels without pinning versions:

```yaml
channels:
  - conda-forge
  - bioconda

dependencies:
  - samtools
```

Exact versions are managed by `conda-lock` rather than pinned in the YML directly.
This separates intent (what tool is needed) from reproducibility (exactly what gets installed).

The filename must match the exact conda package name: `<package-name>_env.yml`. For example,
`kmer-jellyfish_env.yml` for the `kmer-jellyfish` package.

---

## Checking Tool Versions

To see the resolved version of every tool across all lockfiles:

```bash
python get_versions.py
```

To insert or update a version table at the top of the README:

```bash
python get_versions.py --update-readme
```

The table is wrapped in HTML comment markers so subsequent runs replace it cleanly
without affecting any surrounding content. The markers are invisible in rendered Markdown.

To report versions for specific tools only:

```bash
python get_versions.py --tools samtools biopython
```

All flags and their defaults:

```
--containers-dir   Directory containing per-tool subdirectories   (default: containers/)
--readme           Path to the README to update                   (default: README.md)
--tools            Only report versions for the specified tools
--update-readme    Insert or update the version table in the README
```

## Dockerfile

Each tool directory contains a Dockerfile generated from `template.txt`. The full template is:

```dockerfile
FROM mambaorg/micromamba:latest

COPY --chown=$MAMBA_USER:$MAMBA_USER conda-lock.yml /conda-lock.yml

RUN micromamba install -y -n base --freeze-installed -f /conda-lock.yml && micromamba clean --all --yes

USER root

# required for nextflow trace
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

USER $MAMBA_USER

# required for nextflow singularity exec compatibility
ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"
```

**Line by line:**

`FROM mambaorg/micromamba:latest` — uses the official micromamba base image, which provides
a minimal environment with micromamba pre-installed for fast conda package management.

`COPY --chown=$MAMBA_USER:$MAMBA_USER conda-lock.yml /conda-lock.yml` — copies the lockfile
into the image with correct ownership so micromamba can read it without permission issues.
`$MAMBA_USER` is defined by the base image.

`RUN micromamba install -y -n base --freeze-installed -f /conda-lock.yml && micromamba clean --all --yes` —
installs packages into the base environment directly from the lockfile. `--freeze-installed`
skips dependency resolution entirely, making builds fast and fully deterministic. The `clean`
call removes package caches to keep the image size down.

`USER root` — temporarily switches to root to install system packages, which micromamba cannot
manage.

`RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*` — installs
`procps`, which provides utilities like `ps` required by Nextflow for process tracing. The
cache is removed afterward to minimise image size.

`USER $MAMBA_USER` — switches back to the unprivileged micromamba user for runtime, following
the principle of least privilege.

`ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"` — explicitly adds the micromamba environment to
`PATH`. Required for Nextflow compatibility: Nextflow uses `singularity exec` which bypasses
the micromamba entrypoint script, meaning without this line the installed tools would not be
found at runtime.

---

## GitHub Actions

### `build.yml` — Build and publish on change

Triggers on any push to `main` where files outside of `.github/workflows/build.yml`,
`README.md`, `.py`, and `.txt` files have changed.

Uses `git diff` to identify which tool directories under `containers/` changed, then builds
and pushes only those images in parallel (up to 4 at a time). Images are tagged with both
`:latest` and the commit SHA:

```
ghcr.io/bf528/<tool>:latest
ghcr.io/bf528/<tool>:<commit-sha>
```

`:latest` is what students use. The SHA tag provides a stable reference for debugging or
pinning to a known-good version if needed.

### `update_lockfiles.yml` — Annual lockfile refresh

Runs automatically on **August 1st** before the fall semester, and can be triggered manually
via `workflow_dispatch`. To update a single tool rather than all:

1. Go to Actions → Update conda lockfiles → Run workflow
2. Enter the tool directory name in the `tool` input field

The workflow regenerates `conda-lock.yml` for each tool directory, collects per-tool
success/failure without halting on a single error, and opens a pull request summarising
what changed and what failed. Failed tools retain their existing lockfile — their images
continue to build against the last known good state until the issue is resolved manually.

Merging the PR triggers `build.yml` automatically, rebuilding only the affected images.

---

## Image Tags

| Tag | Purpose |
|-----|---------|
| `:latest` | Always points to the most recent build — use this in course materials |
| `:<sha>` | Pinned to a specific commit — use for debugging or rollback |

---

## TO DO

- CI/CD testing for images
- Utilize `docker/metadata-action` to automate label and tag management
- Automate generation of env YML descriptions