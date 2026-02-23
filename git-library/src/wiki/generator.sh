#!/bin/bash
# generator.sh : Moteur de documentation interactive pour git-library
set -euo pipefail

generate_wiki_entry() {
    local target=$1
    local type=$2
    local wiki_file=""
    
    if [ "$type" == "directory" ]; then
        wiki_file="$target/GEMINI.md"
    else
        wiki_file="GEMINI.md"
    fi

    echo "🧠 Génération du Code Wiki pour $target..."
    {
        echo "# 🧠 Code Wiki : $(basename "$target")"
        echo "Généré le : $(date +'%d %b %Y')"
        echo "Type : $type"
        echo "---"
        
        echo "## 🗺️ Architecture Visuelle"
        echo '```mermaid'
        echo "graph TD"
        if [ "$type" == "directory" ]; then
            # Génération d'un diagramme simple basé sur les dossiers de premier niveau
            find "$target" -maxdepth 1 -type d | sed "s|^$target/||" | while read -r dir; do
                if [[ "$dir" != "." && "$dir" != "$target" && "$dir" != "node_modules" && "$dir" != ".git" ]]; then
                    echo "    Root --> $dir"
                fi
            done
        else
            echo "    File --> $(basename "$target")"
        fi
        echo '```'
        echo ""

        echo "## 🔍 Aperçu du Contenu"
        if [ "$type" == "directory" ]; then
            echo "Top 10 fichiers/dossiers :"
            ls -R "$target" | head -n 12 | sed 's/^/    /'
        else
            echo "Fichier unique : $(basename "$target")"
            head -n 20 "$target" | sed 's/^/    /'
        fi
        echo ""

        echo "## 🤖 Aide Agentique"
        echo "Utilisez 'git-library chat $target' pour poser des questions sur ce code."
    } >> "$wiki_file"
}
