#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Lukas Körber
# SPDX-License-Identifier: MIT

# Installs the pinned, hash-locked requirements the way CI does (ci-workflows hacs-ci.yml).
# Runs in the Codespaces prebuild and again on open when the prebuild is older than the last
# change, so a new Codespace starts with everything installed.
set -euo pipefail

cd "$(dirname "$0")/.."

python -m pip install --require-hashes -r requirements_test.txt -r requirements_lint.txt
