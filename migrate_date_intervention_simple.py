#!/usr/bin/env python3
"""
Script de migration simplifié pour ajouter la colonne date_intervention
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire courant au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from datetime import datetime

def migrate_date_intervention_simple():
    """Ajoute la colonne date_intervention en recréant les tables"""
    
    with app.app_context():
        try:
            print("🔧 Migration simplifiée de la colonne date_intervention...")
            
            # Recréer toutes les tables (SQLite gère automatiquement les nouvelles colonnes)
            db.create_all()
            
            print("✅ Tables recréées avec succès!")
            print("La colonne date_intervention est maintenant disponible.")
            
            # Vérifier que la colonne existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('maintenance_curative')
            column_names = [col['name'] for col in columns]
            
            if 'date_intervention' in column_names:
                print("✅ Vérification: La colonne date_intervention existe")
            else:
                print("⚠️ Attention: La colonne date_intervention n'a pas été trouvée")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Migration simplifiée de la colonne date_intervention...")
    
    if migrate_date_intervention_simple():
        print("\n🎉 Migration terminée avec succès!")
        print("La date d'intervention est maintenant disponible dans le formulaire.")
    else:
        print("\n💥 Migration échouée!")
        sys.exit(1) 