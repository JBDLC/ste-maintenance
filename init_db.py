#!/usr/bin/env python3
"""
Script d'initialisation de la base de données PostgreSQL
Utilisez ce script pour créer les tables dans votre base PostgreSQL
"""

import os
from dotenv import load_dotenv
from app import app, db

load_dotenv()

def init_database():
    """Initialise la base de données avec toutes les tables"""
    with app.app_context():
        print("Création des tables de la base de données...")
        db.create_all()
        print("✅ Tables créées avec succès!")
        
        # Vérifier les tables créées
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables disponibles : {', '.join(tables)}")

if __name__ == '__main__':
    init_database() 