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

    echo "🤖 Agent git-library prêt (Mode API Sécurisé)."
    echo "Analyse du contexte dans $wiki_path..."
    
    # Vérification de la clé API
    if [ -z "${GEMINI_API_KEY:-}" ]; then
        echo "⚠️  Variable GEMINI_API_KEY non définie. Passage en mode simulation."
        local mode="SIMULATION"
    else
        local mode="REAL_API"
    fi

    echo "Posez vos questions sur '$target_dir' (tapez 'exit' pour quitter)."
    
    while true; do
        read -p "👤 Vous : " user_query
        [[ "$user_query" == "exit" ]] && break

        if [ "$mode" == "REAL_API" ]; then
            echo "🤖 Agent (API) : Appel à Gemini en cours..."
            # Extraction du contexte du Wiki pour enrichir le prompt
            local context=$(head -n 50 "$wiki_path" | tr '\n' ' ')
            
            # Appel API via Curl (Structure simplifiée)
            curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GEMINI_API_KEY" \
                -H 'Content-Type: application/json' \
                -d "{
                    \"contents\": [{
                        \"parts\":[{
                            \"text\": \"Context: $context. User Question: $user_query\"
                        }]
                    }]
                }" | grep -oP '"text":\s*"\K[^"]+' || echo "❌ Erreur API."
        else
            echo "🤖 Agent (Sim) : Basé sur le contexte $(export | grep CURRENT_SKILLS || echo 'Standard'), votre question sur '$user_query' semble pertinente."
        fi
    done
}
