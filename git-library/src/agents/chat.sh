#!/bin/bash
# chat.sh : Discuter avec sa base de code localement
set -euo pipefail

chat_with_code() {
    local target_dir=$1
    local wiki_path="$target_dir/GEMINI.md"

    if [ ! -d "$target_dir" ]; then
        echo "❌ Erreur : Le dossier '$target_dir' n'existe pas."
        return 1
    fi

    echo "🤖 Agent git-library prêt (Mode Simulation)."
    echo "Analyse du contexte dans $wiki_path..."
    
    if [ -f "$wiki_path" ]; then
        head -n 10 "$wiki_path"
    fi

    echo "Posez vos questions sur '$target_dir' (tapez 'exit' pour quitter)."
    
    while true; do
        read -p "👤 Vous : " user_query
        [[ "$user_query" == "exit" ]] && break

        echo "🤖 Agent : (Simulation) Je vois que vous posez une question sur '$user_query'. En tant qu'IA, je peux vous dire que ce dossier contient des éléments identifiés comme $(export | grep CURRENT_SKILLS || echo 'Standard')."
    done
}
