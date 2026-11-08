#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Lukas Körber
# SPDX-License-Identifier: MIT

# Prints the first steps whenever an editor attaches to the dev container.
set -euo pipefail

if [ -n "${CODESPACE_NAME:-}" ]; then
  url="https://${CODESPACE_NAME}-8123.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
else
  url="http://localhost:8123"
fi

cat <<MSG

Lagersystem dev container
  Run the tests (as CI does):
    pytest tests/ -v --cov=custom_components/lagersystem --cov-report=json:coverage.json
  Lint (as CI does):
    ruff check . && ruff format --check .
  Start Home Assistant with this integration loaded from the checkout:
    scripts/develop
  Then open: ${url}
  The first start takes a few minutes (Home Assistant installs missing requirements into
  config/deps); onboarding creates a local owner account.

MSG
