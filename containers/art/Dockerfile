FROM ubuntu:22.04

LABEL description="ART Illumina read simulator (MountRainier 2016.06.05)"
LABEL version="2016.06.05"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    libgsl27 \
    libgslcblas0 \
    && rm -rf /var/lib/apt/lists/*

# Download and install ART binary
RUN wget -q https://www.niehs.nih.gov/sites/default/files/2024-02/artbinmountrainier2016.06.05linux64.tgz \
    -O /tmp/art.tgz \
    && tar xfz /tmp/art.tgz -C /opt \
    && rm /tmp/art.tgz

# Add ART binaries to PATH
ENV PATH="/opt/art_bin_MountRainier:${PATH}"

WORKDIR /data

CMD ["art_illumina"]