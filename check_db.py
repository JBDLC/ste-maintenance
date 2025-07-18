#!/usr/bin/env python3
"""
Script de vérification de la connexion PostgreSQL
"""

import os
from app import app, db

def check_database():
    """Vérifie la connexion à la base de données"""
    with app.app_context():
        try:
            # Tester la connexion
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Connexion PostgreSQL réussie!")
            
            # Vérifier les tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables disponibles: {', '.join(tables)}")
            
            # Vérifier la configuration
            print(f"🔧 URI de base de données: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False

if __name__ == '__main__':
    check_database() 