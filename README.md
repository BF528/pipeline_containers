# Monorepo for Docker containers used in BF528 - Applications in Translational Bioinformatics

## TO DO

- Utilize docker/metadata action to parse label and tags for images automatically 
- Come up with a better script / strategy for generating the initial repo structure
- CI/CD testing for images?
- Test ignore paths? Should not detect changes in .github or envs/
- Automate generation of YML environment descriptions

## Overview

This repo contains all of the containers and their specifications required for use in BF528. 
For the moment, only tools and packages installable via micromamba are used here. Each container
is built from a templated Dockerfile using a specific YML specification following the style:

```
channels:
- conda-forge
- bioconda

dependencies:
- <tool>=<version>
```

The generage_directory.py script must be run prior to generating the repo. It searches the envs/
directory and creates subdirectories named by the tool containing the Dockerfile and the corresponding
environment specification, `<tool>_env.yml`. The templated dockerfile is stored as template.txt and 
contains a templated value that is replaced with the name of each appropriate YML. 

## Requirements

For this strategy to work:
- The repository must be made public (packages inherit the repo visibility)
- The generage_directory.py script must be run before repo setup and by placing all of the desired
  environment specification YMLs.


## Github Actions

This repo is setup with Github Actions that detects when any file changes in a sub-directory and
automatically rebuilds the image and pushes to the Github Container Registry for only the container
within the sub-directory that changed. Either a YML specification or Dockerfile change will trigger
these actions. 

## Dockerfile

The dockerfile uses micromamba as a base, and requires the following line to work nicely with nextflow:
ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH". Nextflow uses the `singularity exec` command and bypasses the
micromamba entrypoint command. 
