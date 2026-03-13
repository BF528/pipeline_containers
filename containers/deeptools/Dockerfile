FROM mambaorg/micromamba:latest

COPY --chown=$MAMBA_USER:$MAMBA_USER conda-lock.yml /conda-lock.yml

RUN micromamba install -y -n base --freeze-installed -f /conda-lock.yml && micromamba clean --all --yes

USER root

# required for nextflow trace
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

USER $MAMBA_USER

# required for nextflow singularity exec compatibility
ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"