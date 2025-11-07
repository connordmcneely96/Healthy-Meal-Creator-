# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/universal:2

# Install pnpm globally and ensure supporting tools are available
RUN npm install -g pnpm \
    && apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify Python version (3.10+) is available via the base image
RUN python3 --version && pnpm --version
