#!/bin/bash
# downloader.sh : Logique sparse-checkout et curl pour git-library
set -euo pipefail

# Fonction pour récupérer le contenu (Fichiers ou Dossiers)
fetch_content() {
    local url=$1
    local custom_name="${2:-}"
    
    # Détection Fichier (blob)
    if [[ "$url" =~ ^https://github.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$ ]]; then
        local raw="https://raw.githubusercontent.com/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}/${BASH_REMATCH[3]}/${BASH_REMATCH[4]}"
        local filename="${custom_name:-$(basename "${BASH_REMATCH[4]}")}"
        
        # Appel au Policy Engine avant téléchargement
        evaluate_security "$filename"
        
        echo "⬇️ Téléchargement du fichier : $filename..."
        if curl -fsSL "$raw" -o "$filename"; then
            echo "✅ Fichier '$filename' récupéré."
            # Appel au Wiki Generator
            generate_wiki_entry "$filename" "file"
        else
            echo "❌ Erreur : Échec du téléchargement du fichier."
            exit 2
        fi

    # Détection Dossier (tree)
    elif [[ "$url" =~ ^https://github.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)$ ]]; then
        local repo="https://github.com/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}.git"
        local path="${BASH_REMATCH[4]}"
        local out_dir="${custom_name:-$(basename "$path")}"
        
        echo "🚀 Récupération du dossier : $out_dir via Sparse-Checkout..."
        
        local tmp; tmp=$(mktemp -d)
        # Utilisation de clone partiel pour la légèreté
        if ! git clone --depth=1 --filter=blob:none --sparse "$repo" "$tmp"; then
            echo "❌ Erreur : Échec du clonage Git."
            rm -rf "$tmp"
            exit 3
        fi
        
        cd "$tmp"
        if ! git sparse-checkout set "$path"; then
            echo "❌ Erreur : Échec du sparse-checkout."
            cd - > /dev/null
            rm -rf "$tmp"
            exit 1
        fi
        cd - > /dev/null
        
        mv "$tmp/$path" "./$out_dir"
        rm -rf "$tmp"
        
        echo "✅ Dossier '$out_dir' récupéré."
        # Analyse des compétences et génération du Wiki
        identify_skills "./$out_dir"
        generate_wiki_entry "./$out_dir" "directory"
        
        # Exécution des hooks post-téléchargement
        run_hook "after_download" "./$out_dir"
        
    else
        echo "❌ Erreur : Format d'URL GitHub invalide."
        exit 1
    fi
}
