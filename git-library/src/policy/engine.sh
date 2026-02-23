#!/bin/bash
# engine.sh : Moteur de sécurité pour git-library
set -euo pipefail

# États de décision : ALLOW, DENY, ASK_USER
evaluate_security() {
    local target_path=$1
    local extension="${target_path##*.}"
    
    # 1. Règle DENY : Bloquer les fichiers système sensibles
    if [[ "$target_path" == *".ssh/"* || "$target_path" == *".env"* ]]; then
        echo "❌ POLICY DENY : Accès bloqué aux fichiers sensibles ($target_path)."
        exit 1
    fi

    # 2. Règle ASK_USER : Scripts exécutables
    case "$extension" in
        sh|py|js|rb|exe|bat|ps1)
            echo "⚠️  ATTENTION : Vous téléchargez un script exécutable ($target_path)."
            read -p "Voulez-vous autoriser ce fichier sur votre machine ? [y/N] " choice
            if [[ ! "$choice" =~ ^[Yy]$ ]]; then
                echo "🚫 Action annulée par l'utilisateur."
                exit 1
            fi
            ;;
        *)
            # 3. Règle ALLOW : Autres fichiers
            return 0
            ;;
    esac
}
