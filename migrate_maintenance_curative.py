#!/usr/bin/env python3
"""
Script de migration pour ajouter les tables de maintenance curative
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire courant au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def migrate_maintenance_curative():
    """Ajoute les tables de maintenance curative à la base de données"""
    
    with app.app_context():
        try:
            print("🔧 Migration des tables de maintenance curative...")
            
            # Créer les nouvelles tables
            db.create_all()
            
            print("✅ Tables de maintenance curative créées avec succès!")
            print("\nTables ajoutées:")
            print("- maintenance_curative")
            print("- piece_utilisee_curative")
            
            # Vérifier que les tables existent
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'maintenance_curative' in tables and 'piece_utilisee_curative' in tables:
                print("✅ Vérification des tables réussie!")
            else:
                print("❌ Erreur: Les tables n'ont pas été créées correctement")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Début de la migration de maintenance curative...")
    
    if migrate_maintenance_curative():
        print("\n🎉 Migration terminée avec succès!")
        print("\nVous pouvez maintenant utiliser la fonctionnalité de maintenance curative.")
    else:
        print("\n💥 Migration échouée!")
        sys.exit(1) 