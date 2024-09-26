FROM mambaorg/micromamba:latest

COPY --chown=$MAMBA_USER:$MAMBA_USER verse_env.yml /verse_env.yml

RUN micromamba install -y -n base -f /verse_env.yml && micromamba clean --all --yes

# just exec things causing problems, not a great fix
ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"