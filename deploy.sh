#!/bin/bash

echo "🚀 Déploiement sur Render.com..."

# Vérifier que tous les fichiers sont présents
echo "📋 Vérification des fichiers..."
if [ ! -f "app.py" ]; then
    echo "❌ app.py manquant"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt manquant"
    exit 1
fi

if [ ! -f "Procfile" ]; then
    echo "❌ Procfile manquant"
    exit 1
fi

if [ ! -f "runtime.txt" ]; then
    echo "❌ runtime.txt manquant"
    exit 1
fi

echo "✅ Tous les fichiers sont présents"

# Afficher les configurations
echo "📋 Configuration actuelle :"
echo "  - Python: $(cat runtime.txt)"
echo "  - Dependencies: $(wc -l < requirements.txt) packages"
echo "  - Procfile: $(cat Procfile)"

echo ""
echo "🎯 Pour déployer sur Render.com :"
echo "1. Poussez ces changements sur votre repository Git"
echo "2. Connectez-vous à Render.com"
echo "3. Créez un nouveau service Web"
echo "4. Connectez votre repository"
echo "5. Le déploiement se fera automatiquement"

echo ""
echo "🔧 Les changements apportés :"
echo "  - Python 3.11.7 (plus stable)"
echo "  - psycopg[binary]==3.1.13 (version fixe)"
echo "  - greenlet==3.0.1 (version compatible)"
echo "  - render.yaml ajouté pour la configuration"

echo ""
echo "✅ Prêt pour le déploiement !" 