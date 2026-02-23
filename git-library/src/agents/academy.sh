#!/bin/bash
# academy.sh : Moteur de génération de tutoriels "Academy" avec Ingestion Sécurisée
set -euo pipefail

# --- Aide à l'Ingestion Sécurisée ---
# Cette fonction génère le JSON de la requête Gemini sans passer par eval/shell interpolation
generate_secure_payload() {
    local prompt_template=$1
    local context_file=$2
    local output_file=$3

    # On cherche un moteur JSON fonctionnel (Node ou Python)
    local engine=""
    if command -v node &> /dev/null && node -v &> /dev/null; then
        engine="node"
    elif command -v python3 &> /dev/null && python3 --version &> /dev/null; then
        engine="python3"
    elif command -v python &> /dev/null && python --version &> /dev/null; then
        engine="python"
    fi

    case "$engine" in
        "node")
            node -e "const fs = require('fs');
const context = fs.readFileSync(process.argv[2], 'utf8');
const prompt = process.argv[1].replace('{{CONTEXT}}', context);
console.log(JSON.stringify({contents: [{parts: [{text: prompt}]}]}));" "$prompt_template" "$context_file" > "$output_file"
            ;;
        "python3"|"python")
            $engine -c "import json, sys; 
context = open(sys.argv[2], 'r', encoding='utf-8').read();
prompt = sys.argv[1].replace('{{CONTEXT}}', context);
print(json.dumps({'contents': [{'parts': [{'text': prompt}]}]}))" "$prompt_template" "$context_file" > "$output_file"
            ;;
        *)
            echo "❌ Erreur : Python ou Node.js fonctionnel requis."
            return 1
            ;;
    esac
}

# Fonction pour identifier les abstractions principales du projet
extract_abstractions() {
    local target=$1
    local context_file=$(mktemp)
    head -n 200 "$target/GEMINI.md" > "$context_file" 2>/dev/null || echo "Standard project" > "$context_file"
    
    if [ -z "${GEMINI_API_KEY:-}" ]; then
        echo "❌ Erreur : GEMINI_API_KEY n'est pas définie."
        rm -f "$context_file"
        return 1
    fi

    echo "🧠 Identification des piliers logiques du projet (Mode Sécurisé)..."
    
    local prompt_template="Analysez ce projet basé sur ce contexte :
---
{{CONTEXT}}
---
Identifiez les 5 concepts techniques les plus fondamentaux pour un débutant.
Pour chaque concept, fournissez :
1. Un 'name' clair.
2. Une 'description' pédagogique (100 mots) incluant une ANALOGIE concrète.
3. Les 'files' (symboles ou fichiers) concernés.

Formatte l'output en YAML strict :
- name: ...
  description: ...
  files: [...]"

    local payload_file=$(mktemp)
    generate_secure_payload "$prompt_template" "$context_file" "$payload_file"

    local response=$(curl -s -f -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
        -H 'Content-Type: application/json' \
        -d @"$payload_file") || {
            echo "❌ Erreur : L'appel API a échoué."
            rm -f "$context_file" "$payload_file"
            return 1
        }
    
    rm -f "$context_file" "$payload_file"

    # Extraction YAML
    local content=$(echo "$response" | sed -n 's/.*"text": "\(.*\)".*/\1/p')
    local clean_content=$(echo "$content" | sed 's/\\n/\n/g' | sed 's/```yaml//g' | sed 's/```//g')
    
    echo "$clean_content"
}

# Fonction pour rédiger un chapitre
write_chapter() {
    local project_name=$1
    local chapter_num=$2
    local concept_name=$3
    local concept_desc=$4
    local output_dir=$5

    echo "✍️ Rédaction du Chapitre $chapter_num : $concept_name..."
    
    local prompt="Projet: $project_name. Chapitre $chapter_num sur $concept_name. Description: $concept_desc. Rédigez un chapitre de tutoriel pédagogique complet en Markdown. Incluez une analogie, des explications simples et un mini exemple de code fictif. Langage: Français."

    local payload_file=$(mktemp)
    # Pour les prompts courts sans contextes lourds, on peut rester simple ou réutiliser generate_secure_payload
    python3 -c "import json, sys; print(json.dumps({'contents': [{'parts': [{'text': sys.argv[1]}]}]}))" "$prompt" > "$payload_file" 2>/dev/null || \
    node -e "console.log(JSON.stringify({contents: [{parts: [{text: process.argv[1]}]}]}))" "$prompt" > "$payload_file"

    local response=$(curl -s -f -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
        -H 'Content-Type: application/json' \
        -d @"$payload_file") || return 1
    
    rm -f "$payload_file"

    local content=$(echo "$response" | sed -n 's/.*"text": "\(.*\)".*/\1/p' | sed 's/\\n/\n/g')
    
    local safe_name=$(echo "$concept_name" | sed 's/[^a-zA-Z0-9]/_/g' | tr '[:upper:]' '[:lower:]')
    local filename="chapter_${chapter_num}_${safe_name}.md"
    
    echo "$content" > "$output_dir/$filename"
}

# Fonction principale 'teach'
run_academy() {
    local target=$1
    local project_name=$(basename "$target")
    local timestamp=$(date +'%Y-%m-%d_%H-%M')
    local academy_dir="$VAULT_DIR/$project_name/$timestamp/academy"
    
    mkdir -p "$academy_dir"
    
    echo "🎓 Bienvenue à la Git-Library Academy pour $project_name !"
    
    # 1. Extraction des piliers
    local abstractions=$(extract_abstractions "$target")
    
    # 2. Génération des chapitres
    local i=1
    while read -r line; do
        if [[ "$line" =~ ^-?[[:space:]]*name:[[:space:]]*(.*) ]]; then
            local name="${BASH_REMATCH[1]}"
            read -r desc_line
            if [[ "$desc_line" =~ [[:space:]]*description:[[:space:]]*(.*) ]]; then
                local desc="${BASH_REMATCH[1]}"
                write_chapter "$project_name" "$i" "$name" "$desc" "$academy_dir"
                ((i++))
            fi
        fi
    done <<< "$abstractions"
    
    # 3. Indexation
    local index_file="$academy_dir/ACADEMY.md"
    echo "# 🎓 Academy : $project_name" > "$index_file"
    echo "Généré le $(date)" >> "$index_file"
    echo "" >> "$index_file"
    echo "## Sommaire" >> "$index_file"
    ls "$academy_dir" | grep "chapter_" | while read -r f; do
        echo "- [$f](./$f)" >> "$index_file"
    done
    
    echo "🎉 Academy terminée ! Dossier : $academy_dir"
}
