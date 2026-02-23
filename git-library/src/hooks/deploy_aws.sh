#!/bin/bash
# deploy_aws.sh : Hook intelligent pour déploiement AWS (S3/Static)
set -euo pipefail

echo "☁️  Vérification de l'environnement AWS pour : $LIB_TARGET"

if ! command -v aws &> /dev/null; then
    echo "⚠️  AWS CLI non détecté."
    echo "💡 Action requise : Installez AWS CLI et configurez vos credentials ('aws configure')."
    exit 1
fi

if [ -z "${AWS_S3_BUCKET:-}" ]; then
    echo "⚠️  Variable AWS_S3_BUCKET non définie."
    echo "💡 Action requise : Exportez 'AWS_S3_BUCKET' pour activer le déploiement S3."
    exit 1
fi

echo "🚀 Synchronisation vers S3 : s3://$AWS_S3_BUCKET..."
aws s3 sync "$LIB_TARGET" "s3://$AWS_S3_BUCKET" --delete
