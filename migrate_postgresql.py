#!/usr/bin/env python3
"""
Script de migration PostgreSQL pour ajouter la colonne date_intervention
À utiliser en production avec PostgreSQL
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

def migrate_postgresql():
    """Migration pour PostgreSQL en production"""
    
    with app.app_context():
        try:
            print("🔧 Migration PostgreSQL de la colonne date_intervention...")
            
            # Vérifier si on est sur PostgreSQL
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            if 'postgresql' not in db_url.lower():
                print("⚠️ Attention: Ce script est conçu pour PostgreSQL")
                print(f"Base de données actuelle: {db_url}")
                return False
            
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
                # D'abord ajouter la colonne sans contrainte NOT NULL
                conn.execute(db.text("""
                    ALTER TABLE maintenance_curative 
                    ADD COLUMN date_intervention DATE
                """))
                
                # Mettre à jour les enregistrements existants
                conn.execute(db.text("""
                    UPDATE maintenance_curative 
                    SET date_intervention = date_realisation::date 
                    WHERE date_intervention IS NULL
                """))
                
                # Ajouter la contrainte NOT NULL
                conn.execute(db.text("""
                    ALTER TABLE maintenance_curative 
                    ALTER COLUMN date_intervention SET NOT NULL
                """))
                
                # Ajouter une valeur par défaut pour les futures insertions
                conn.execute(db.text("""
                    ALTER TABLE maintenance_curative 
                    ALTER COLUMN date_intervention SET DEFAULT CURRENT_DATE
                """))
                
                conn.commit()
            
            print("✅ Colonne date_intervention ajoutée avec succès!")
            
            # Vérifier que la colonne existe maintenant
            columns = inspector.get_columns('maintenance_curative')
            column_names = [col['name'] for col in columns]
            
            if 'date_intervention' in column_names:
                print("✅ Vérification: La colonne date_intervention existe")
            else:
                print("❌ Erreur: La colonne date_intervention n'a pas été créée")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Migration PostgreSQL de la colonne date_intervention...")
    
    if migrate_postgresql():
        print("\n🎉 Migration terminée avec succès!")
        print("La date d'intervention est maintenant disponible dans le formulaire.")
    else:
        print("\n💥 Migration échouée!")
        sys.exit(1) 