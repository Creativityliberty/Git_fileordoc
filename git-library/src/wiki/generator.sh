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

        echo "## 📂 Structure du Projet"
        if command -v tree &> /dev/null; then
            tree -L 3 "$target" -I "node_modules|.git" | sed 's/^/    /'
        else
            find "$target" -maxdepth 3 -not -path '*/.*' -not -path '*node_modules*' | sed "s|^$target/||" | sed 's/^/    /'
        fi
        echo ""

        # Section Academy si disponible
        local project_name=$(basename "$target")
        if [ -d "$VAULT_DIR/$project_name" ]; then
            echo "## 🎓 Academy & Tutoriels"
            find "$VAULT_DIR/$project_name" -name "ACADEMY.md" | sort -r | head -n 1 | while read -r academy_index; do
                local rel_path=$(realpath --relative-to="$target" "$academy_index" 2>/dev/null || echo "$academy_index")
                echo "Un parcours d'apprentissage est disponible pour ce projet."
                echo "- [Voir l'Academy]($rel_path)"
            done
            echo ""
        fi

        # Append surgical data if available
        if [ -n "${SURGICAL_SYMBOLS:-}" ]; then
            echo -e "## 🩺 Symboles Chirurgicaux (Classes & Fonctions)"
            echo -e "\`\`\`text\n$SURGICAL_SYMBOLS\n\`\`\`"
        fi

        echo "## 🤖 Aide Agentique"
        echo "Utilisez 'git-library chat $target' pour poser des questions sur ce code."
    } >> "$wiki_file"

    # Génération du GEMINI.json (AI-Native) - Version robuste
    local json_path="${target%/}/GEMINI.json"
    cat <<EOF > "$json_path"
{
  "project": "$(basename "$target")",
  "type": "$type",
  "generated_at": "$(date +'%Y-%m-%d %H:%M:%S')",
  "surgical_data": {
    "symbols_count": $(echo "$SURGICAL_SYMBOLS" | wc -l),
    "dependencies_count": $(echo "$SURGICAL_DEPS" | wc -l)
  },
  "academy": {
    "status": "pending_api_key_verification"
  }
}
EOF
    echo "🤖 Fichier JSON généré : $json_path"

    # --- ARCHIVAGE DANS LE VAULT (STRUCTURE 3 PILIERS) ---
    if [ -n "${VAULT_DIR:-}" ]; then
        local timestamp=$(date +'%Y-%m-%d_%H-%M')
        local project_name=$(basename "$target")
        local session_vault="$VAULT_DIR/$project_name/$timestamp"
        
        # Noms des piliers (selon demande utilisateur)
        local bridge_dir="$session_vault/1. Pont - Code vers IA"
        local surgeon_dir="$session_vault/2. Chirurgien - Analyse Chirurgicale"
        local academy_dir="$session_vault/3. Elite Academy"
        
        # Création des piliers
        mkdir -p "$bridge_dir"
        mkdir -p "$surgeon_dir"
        mkdir -p "$academy_dir"
        
        # Déplacement/Copie des fichiers vers les bons piliers
        cp "$wiki_file" "$bridge_dir/GEMINI.md"
        [ -f "$json_path" ] && cp "$json_path" "$surgeon_dir/GEMINI.json"
        
        # Mise à jour de l'INDEX.md du Vault (Plus propre)
        local index_file="$VAULT_DIR/INDEX.md"
        [ ! -f "$index_file" ] && echo "# 🏛️ Intelligence Vault Index" > "$index_file"
        if ! grep -q "$project_name" "$index_file"; then
            echo "- **$project_name** : [Dernière analyse](./$project_name/$timestamp/1.%20Pont%20-%20Code%20vers%20IA/GEMINI.md)" >> "$index_file"
        fi

        echo "🏛️ Session archivée dans le Vault (3 piliers) : $session_vault"
        
        # Export pour le moteur Academy
        export CURRENT_ACADEMY_DIR="$academy_dir"
    fi

    echo "✅ Documentation générée : $wiki_file"
}
