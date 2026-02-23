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

    # Génération du GEMINI.json (AI-Native)
    local json_path="${target%/}/GEMINI.json"
    local json_content="{\"project\": \"$(basename "$target")\", \"type\": \"$type\", \"skills\": \"${CURRENT_SKILLS:-None}\", \"symbols\": \"$(echo "$SURGICAL_SYMBOLS" | tr '\n' ' ')\", \"dependencies\": \"$(echo "$SURGICAL_DEPS" | tr '\n' ' ')\"}"
    if [ "$type" == "directory" ]; then
        echo "$json_content" > "$json_path"
        echo "🤖 Fichier JSON généré : $json_path"
    fi

    # --- ARCHIVAGE DANS LE VAULT ---
    if [ -n "${VAULT_DIR:-}" ]; then
        local project_name=$(basename "$target")
        local timestamp=$(date +'%Y-%m-%d_%H-%M')
        local archive_dir="$VAULT_DIR/$project_name/$timestamp"
        mkdir -p "$archive_dir"
        
        cp "$wiki_file" "$archive_dir/GEMINI.md"
        [ -f "$json_path" ] && cp "$json_path" "$archive_dir/GEMINI.json"
        
        # Extraction du Mermaid en fichier séparé
        sed -n '/```mermaid/,/```/p' "$wiki_file" > "$archive_dir/architecture.mmd"
        
        # Mise à jour de l'INDEX.md du Vault
        local index_file="$VAULT_DIR/INDEX.md"
        if [ ! -f "$index_file" ]; then
            echo "# 🏛️ Intelligence Vault Index" > "$index_file"
        fi
        if ! grep -q "$project_name" "$index_file"; then
            echo "- **$project_name** : [Dernière analyse](./$project_name/$timestamp/GEMINI.md)" >> "$index_file"
        fi
        
        echo "🏛️ Archivé dans le Vault : $archive_dir"
    fi

    echo "✅ Documentation générée : $wiki_file"
}
