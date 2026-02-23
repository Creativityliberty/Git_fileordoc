#!/bin/bash
# surgeon.sh : Module d'analyse chirurgicale pour git-library
set -euo pipefail

# Fonction pour extraire les symboles (Classes, Fonctions)
extract_symbols() {
    local target=$1
    echo "🩺 Dissection des symboles dans : $target..."
    
    # Extraction simplifiée via grep/sed (adaptable par Skill)
    # Cherche 'class Name', 'def name', 'function name', 'func name'
    if [ -d "$target" ]; then
        grep -rE "class [a-zA-Z0-9_]+|def [a-zA-Z0-9_]+|function [a-zA-Z0-9_]+|func [a-zA-Z0-9_]+" "$target" \
            --exclude-dir=node_modules --exclude-dir=.git \
            | sed 's/^.*: //' | sort | uniq
    else
        grep -E "class [a-zA-Z0-9_]+|def [a-zA-Z0-9_]+|function [a-zA-Z0-9_]+|func [a-zA-Z0-9_]+" "$target" \
            | sed 's/^.*: //' | sort | uniq
    fi
}

# Fonction pour mapper les dépendances
map_dependencies() {
    local target=$1
    echo "🕸️ Mapping des dépendances..."
    
    if [ -d "$target" ]; then
        # Cherche imports/requires
        grep -rE "import .* from|require\(.*\)" "$target" \
            --exclude-dir=node_modules --exclude-dir=.git \
            | sed 's/^.*: //' | sort | uniq
    fi
}

# Fonction principale de chirurgie
run_surgery() {
    local target=$1
    echo "--- DEBUT DE LA CHIRURGIE : $target ---"
    
    local symbols=$(extract_symbols "$target")
    local deps=$(map_dependencies "$target")
    
    # Export pour le Wiki Generator
    export SURGICAL_SYMBOLS="$symbols"
    export SURGICAL_DEPS="$deps"
    
    echo "✅ Chirurgie terminée. Données prêtes pour l'ingestion."
}
