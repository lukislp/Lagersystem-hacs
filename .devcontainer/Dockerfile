# SPDX-FileCopyrightText: 2026 Lukas Körber
# SPDX-License-Identifier: MIT

# The dev container's base image (devcontainer.json "build"): the tag 3-3.14-bookworm of
# mcr.microsoft.com/devcontainers/python (CI runs on Python 3.14, which Home Assistant 2026.11
# needs), pinned by digest. Digest only, because the Dev Container CLI does not parse
# "tag@digest"; bump by looking the tag up again
# (`docker buildx imagetools inspect mcr.microsoft.com/devcontainers/python:3-3.14-bookworm`).
FROM mcr.microsoft.com/devcontainers/python@sha256:94053b777943a4eda40e83d5386f7c5befb72f5bb778878ac527bb9491adcd42

# The image ships the Yarn apt repository, whose signing key is no longer accepted
# (NO_PUBKEY 62D54FD4003F6525), so every `apt-get update` fails and with it every Dev Container
# feature that installs packages. Nothing here needs Yarn. Remove the source before the features run.
RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn.sources \
    && rm -f /usr/share/keyrings/yarn-archive-keyring.gpg /etc/apt/trusted.gpg.d/yarn.gpg

# Home Assistant's camera, stream and dhcp components need these system libraries.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libturbojpeg0 libpcap0.8 \
    && rm -rf /var/lib/apt/lists/*
