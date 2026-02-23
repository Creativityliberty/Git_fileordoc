#!/bin/bash
# registry.sh : Détecteur de compétences pour git-library
set -euo pipefail

identify_skills() {
    local target_dir=$1
    local identified_skills=()

    echo "🔍 Analyse des compétences dans : $target_dir..."

    # Recherche de signatures techniques
    [ -f "$target_dir/package.json" ] && identified_skills+=("React/NodeJS")
    [ -f "$target_dir/go.mod" ] && identified_skills+=("Go")
    [ -f "$target_dir/requirements.txt" ] || [ -f "$target_dir/pyproject.toml" ] && identified_skills+=("Python")
    [ -f "$target_dir/bun.lockb" ] && identified_skills+=("Bun")
    [ -f "$target_dir/Cargo.toml" ] && identified_skills+=("Rust")
    [ -f "$target_dir/Package.swift" ] && identified_skills+=("Swift")
    [ -f "$target_dir/CMakeLists.txt" ] && identified_skills+=("C++")

    if [ ${#identified_skills[@]} -eq 0 ]; then
        echo "ℹ️ Aucune compétence spécifique détectée. Utilisation du Skill 'default'."
        export CURRENT_SKILLS="Standard"
    else
        echo "🚀 Skills détectés : ${identified_skills[*]}"
        export CURRENT_SKILLS="${identified_skills[*]}"
        apply_skills_to_wiki "$target_dir" "${identified_skills[@]}"
    fi
}

apply_skills_to_wiki() {
    local target_dir=$1
    shift
    local skills=("$@")
    local wiki_file="$target_dir/GEMINI.md"

    {
        echo "## 🛠️ Compétences IA Actives"
        for skill in "${skills[@]}"; do
            echo "* **Skill $skill** : Activé pour l'analyse structurelle."
        done
        echo ""
    } >> "$wiki_file"
}
