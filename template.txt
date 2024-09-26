FROM mambaorg/micromamba:latest

COPY --chown=$MAMBA_USER:$MAMBA_USER <env_desc> /<env_desc>

RUN micromamba install -y -n base -f /<env_desc> && micromamba clean --all --yes

# just exec things causing problems, not a great fix
ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"