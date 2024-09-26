FROM mambaorg/micromamba:latest

COPY --chown=$MAMBA_USER:$MAMBA_USER bowtie2_env.yml /bowtie2_env.yml

RUN micromamba install -y -n base -f /bowtie2_env.yml && micromamba clean --all --yes

# just exec things causing problems, not a great fix
ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"