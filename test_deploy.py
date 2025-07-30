#!/usr/bin/env python3
"""
Script de test simplifié pour vérifier la compatibilité Render.com
"""

import sys

def test_app():
    """Teste que l'application Flask peut démarrer"""
    print("🔍 Test de l'application Flask...")
    
    try:
        # Import de l'app
        from app import app, db
        
        # Test de création des tables
        with app.app_context():
            db.create_all()
            print("✅ Base de données initialisée")
        
        print("✅ Application Flask prête")
        return True
        
    except Exception as e:
        print(f"❌ Erreur application: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de compatibilité pour Render.com")
    print("=" * 50)
    
    if test_app():
        print("\n✅ Application prête pour le déploiement !")
        print("\n📋 Prochaines étapes:")
        print("1. git add .")
        print("2. git commit -m 'Fix: psycopg2-binary pour Render.com'")
        print("3. git push origin main")
        print("4. Vérifier le déploiement sur Render.com")
    else:
        print("\n❌ Erreur dans l'application. Corriger avant le déploiement.")
        sys.exit(1)

if __name__ == "__main__":
    main() 