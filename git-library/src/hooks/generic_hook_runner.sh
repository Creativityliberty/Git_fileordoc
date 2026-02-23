#!/bin/bash
# lifecycle.sh / hooks manager : Gestion des hooks pour git-library
set -euo pipefail

run_hook() {
    local event=$1
    local target=$2
    local hook_script="${CONFIG_DIR:-$HOME/.gemini}/hooks/$event.sh"

    if [ -f "$hook_script" ]; then
        echo "🪝  Exécution du hook : $event pour $target..."
        export LIB_TARGET="$target"
        # On lance le hook dans un sous-shell pour ne pas polluer l'actuel
        bash "$hook_script" || echo "⚠️  Le hook $event a rencontré une erreur mais l'exécution continue."
    fi
}
