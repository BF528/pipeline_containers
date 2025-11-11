FROM ubuntu:rolling

RUN apt-get update && apt-get install -y procps wget && rm -rf /var/lib/apt/lists/*

WORKDIR /bin

RUN wget https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.2.1/sratoolkit.3.2.1-ubuntu64.tar.gz && \
    tar -xvzf sratoolkit.3.2.1-ubuntu64.tar.gz && \
    rm sratoolkit.3.2.1-ubuntu64.tar.gz

ENV PATH="/bin/sratoolkit.3.2.1-ubuntu64/bin:$PATH"