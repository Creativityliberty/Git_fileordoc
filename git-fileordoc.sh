#!/bin/bash

set -euo pipefail

VERSION="1.2.0"
INSTALL_PATH="/usr/local/bin/git-fileordoc"
LOG_FILE="$HOME/.git-fileordoc.log"

# Système de log pour le suivi des opérations
exec 3>>"$LOG_FILE"
log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >&3; }

# Vérification des dépendances (Git et Curl)
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        log "Error: $1 is not installed."
        echo "Error: $1 is required but not installed." >&2
        exit 1
    fi
}

check_dependency "git"
check_dependency "curl"

# Fonction de mise à jour du script
update_script() {
    log "Updating git-fileordoc..."
    if sudo curl -fsSL "https://votre-repo-url/git-fileordoc.sh" -o "$INSTALL_PATH"; then
        sudo chmod +x "$INSTALL_PATH"
        log "Update successful."
        echo "git-fileordoc updated to version $VERSION"
    else
        log "Error: Update failed."
        exit 2
    fi
    exit 0
}

# Fonction de désinstallation
uninstall_script() {
    log "Uninstalling git-fileordoc..."
    if sudo rm -f "$INSTALL_PATH"; then
        log "Uninstallation successful."
        echo "git-fileordoc has been removed."
    else
        log "Error: Uninstallation failed."
        exit 1
    fi
    exit 0
}

# Aide et usage
print_help() {
    echo "Usage: git-fileordoc <GitHub URL> [TARGET_NAME]"
    echo "       git-fileordoc ---update       # Mettre à jour le script"
    echo "       git-fileordoc ---uninstall    # Désinstaller le script"
    echo "       git-fileordoc ---version      # Afficher la version"
    exit 0
}

# Gestion des arguments de commande
case "${1:-}" in
    "---update") update_script ;;
    "---uninstall") uninstall_script ;;
    "---version") echo "git-fileordoc version $VERSION"; exit 0 ;;
    "---help") print_help ;;
    "") echo "Error: No argument provided. Use ---help for usage." >&2; exit 1 ;;
esac

URL="$1"
CUSTOM_NAME="${2:-}" # Upgrade : Nom de sortie personnalisé
log "Processing URL: $URL"

# Fonction pour cloner un dossier spécifique
clone_repo() {
    local REPO_URL="$1"
    local TARGET_PATH="$2"
    local FINAL_NAME="${3:-$(basename "$TARGET_PATH")}" # Utilise le nom custom ou original
    local TEMP_DIR
    TEMP_DIR=$(mktemp -d) # Utilisation d'un dossier temporaire sécurisé
    local CURRENT_DIR=$(pwd)

    log "Cloning repository: $REPO_URL into $TEMP_DIR"
    # Utilisation de clone partiel (depth 1 et filter) pour la légèreté
    if ! git clone --depth=1 --filter=blob:none --sparse "$REPO_URL" "$TEMP_DIR"; then
        log "Error: Git clone failed."
        exit 3
    fi

    cd "$TEMP_DIR"
    log "Setting sparse checkout for $TARGET_PATH"
    # Activation du sparse-checkout pour cibler le dossier
    if ! git sparse-checkout set "$TARGET_PATH"; then
        log "Error: Sparse checkout failed."
        exit 1
    fi

    cd "$CURRENT_DIR"
    # Déplacement vers la destination finale avec le nom choisi
    mv "$TEMP_DIR/$TARGET_PATH" "./$FINAL_NAME"
    rm -rf "$TEMP_DIR" # Nettoyage
    echo "Dossier récupéré avec succès sous : ./$FINAL_NAME"
    exit 0
}

# --- Analyse de l'URL GitHub ---

# Cas 1 : Fichier unique (URL de type 'blob')
if [[ "$URL" =~ ^https://github.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$ ]]; then
    USER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
    BRANCH="${BASH_REMATCH[3]}"
    FILE_PATH="${BASH_REMATCH[4]}"
    RAW_URL="https://raw.githubusercontent.com/$USER/$REPO/$BRANCH/$FILE_PATH"
    OUTPUT_FILE="${CUSTOM_NAME:-$(basename "$FILE_PATH")}"

    log "Fetching raw file from $RAW_URL"
    if curl -fsSL "$RAW_URL" -o "$OUTPUT_FILE"; then
        echo "Fichier téléchargé : $OUTPUT_FILE"
    else
        log "Error: Failed to download file."
        exit 2
    fi
    exit 0

# Cas 2 : Dossier spécifique (URL de type 'tree')
elif [[ "$URL" =~ ^https://github.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)$ ]]; then
    REPO_URL="https://github.com/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}.git"
    TARGET_PATH="${BASH_REMATCH[4]}"
    clone_repo "$REPO_URL" "$TARGET_PATH" "$CUSTOM_NAME"

else
    log "Error: Invalid GitHub URL format."
    echo "Error: Invalid GitHub URL format. Use ---help for details." >&2
    exit 1
fi
