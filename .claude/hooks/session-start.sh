#!/bin/bash
# SessionStart: instala el entorno de simulación (sim/requirements.txt) en sesiones en la nube.
# Idempotente: si los paquetes ya están, pip no descarga nada.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

python3 -m pip install --quiet --disable-pip-version-check --no-input --root-user-action=ignore -r sim/requirements.txt

echo "CanSat Brain: entorno de simulación listo (sim/requirements.txt). Empieza con la skill inicio."
