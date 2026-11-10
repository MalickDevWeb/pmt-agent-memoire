FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    texlive-full \
    latexmk \
    librsvg2-bin \
    python3 \
    python3-pip \
    python3-pil \
    python3-pygments \
    fonts-firacode \
    git \
    curl \
    unzip \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Outil de capture code stylisee (PNG)
RUN curl -L https://github.com/Aloxaf/silicon/releases/latest/download/silicon-linux-musl.tar.gz \
  | tar -xz -C /usr/local/bin silicon
