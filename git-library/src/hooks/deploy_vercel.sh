#!/bin/bash
# deploy_vercel.sh : Hook intelligent pour déploiement Vercel
set -euo pipefail

echo "📡 Vérification de l'environnement Vercel pour : $LIB_TARGET"

if [ ! -f "$LIB_TARGET/vercel.json" ] && [ ! -f "$LIB_TARGET/package.json" ]; then
    echo "ℹ️ Aucune signature Vercel détectée. Ignoré."
    exit 0
fi

if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI non détecté."
    echo "💡 Action requise : Installez-le avec 'npm i -g vercel' pour activer le déploiement auto."
    exit 1
fi

echo "🚀 Déploiement vers Vercel..."
cd "$LIB_TARGET"
vercel --prod
cd - > /dev/null
