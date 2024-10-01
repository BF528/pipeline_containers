FROM mambaorg/micromamba:latest

COPY --chown=$MAMBA_USER:$MAMBA_USER fastqc_env.yml /fastqc_env.yml

RUN micromamba install -y -n base -f /fastqc_env.yml && micromamba clean --all --yes

USER root

# required for nextflow trace
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

USER $MAMBA_USER

# just exec things causing problems, not a great fix
ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"