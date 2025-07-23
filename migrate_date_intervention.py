#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne date_intervention
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

def migrate_date_intervention():
    """Ajoute la colonne date_intervention à la table maintenance_curative"""
    
    with app.app_context():
        try:
            print("🔧 Migration de la colonne date_intervention...")
            
            # Vérifier si la colonne existe déjà
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('maintenance_curative')
            column_names = [col['name'] for col in columns]
            
            if 'date_intervention' in column_names:
                print("✅ La colonne date_intervention existe déjà")
                return True
            
            # Ajouter la colonne (PostgreSQL)
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE maintenance_curative 
                    ADD COLUMN date_intervention DATE NOT NULL DEFAULT CURRENT_DATE
                """))
                conn.commit()
            
            print("✅ Colonne date_intervention ajoutée avec succès!")
            
            # Mettre à jour les enregistrements existants
            from app import MaintenanceCurative
            maintenances = MaintenanceCurative.query.all()
            
            for maintenance in maintenances:
                if not hasattr(maintenance, 'date_intervention') or maintenance.date_intervention is None:
                    # Utiliser la date de réalisation comme date d'intervention par défaut
                    maintenance.date_intervention = maintenance.date_realisation.date()
            
            db.session.commit()
            print(f"✅ {len(maintenances)} enregistrements mis à jour")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Migration de la colonne date_intervention...")
    
    if migrate_date_intervention():
        print("\n🎉 Migration terminée avec succès!")
        print("La date d'intervention est maintenant disponible dans le formulaire.")
    else:
        print("\n💥 Migration échouée!")
        sys.exit(1) 