#!/bin/bash

# Script de déploiement pour Maintenance STE
# Usage: ./deploy.sh "Message de commit"

echo "🚀 Déploiement de Maintenance STE..."

# Vérifier si un message de commit est fourni
if [ -z "$1" ]; then
    echo "❌ Erreur: Veuillez fournir un message de commit"
    echo "Usage: ./deploy.sh \"Message de commit\""
    exit 1
fi

COMMIT_MESSAGE="$1"

# Vérifier si Git est initialisé
if [ ! -d ".git" ]; then
    echo "📁 Initialisation de Git..."
    git init
fi

# Ajouter tous les fichiers
echo "📦 Ajout des fichiers..."
git add .

# Commiter les changements
echo "💾 Commit avec le message: $COMMIT_MESSAGE"
git commit -m "$COMMIT_MESSAGE"

# Vérifier si la branche main existe
if git branch --list | grep -q "main"; then
    echo "🔄 Mise à jour de la branche main..."
    git push origin main
else
    echo "🌿 Création de la branche main..."
    git branch -M main
    git push -u origin main
fi

echo "✅ Déploiement terminé!"
echo "🔗 Vérifiez votre application sur Render dans quelques minutes"
echo "📋 Logs disponibles dans le dashboard Render" 