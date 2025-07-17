#!/usr/bin/env python3
"""
Script de migration pour la base de données PostgreSQL
Utilisez ce script pour migrer des données de SQLite vers PostgreSQL
"""

import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from app import app, db, Site, Localisation, Equipement, Piece, LieuStockage, Maintenance, User

load_dotenv()

def export_sqlite_data():
    """Exporte les données de SQLite vers des fichiers CSV"""
    sqlite_path = 'maintenance.db'
    
    if not os.path.exists(sqlite_path):
        print("❌ Fichier SQLite non trouvé")
        return
    
    print("📤 Export des données SQLite...")
    
    # Connexion à SQLite
    conn = sqlite3.connect(sqlite_path)
    
    # Tables à exporter
    tables = ['site', 'localisation', 'equipement', 'lieu_stockage', 'piece', 'maintenance', 'user']
    
    for table in tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            if not df.empty:
                df.to_csv(f'export_{table}.csv', index=False)
                print(f"✅ {table}: {len(df)} enregistrements exportés")
            else:
                print(f"⚠️  {table}: Aucune donnée")
        except Exception as e:
            print(f"❌ Erreur export {table}: {e}")
    
    conn.close()
    print("📁 Export terminé dans les fichiers CSV")

def import_to_postgresql():
    """Importe les données CSV vers PostgreSQL"""
    print("📥 Import vers PostgreSQL...")
    
    with app.app_context():
        # Créer les tables si elles n'existent pas
        db.create_all()
        
        # Tables à importer (dans l'ordre des dépendances)
        tables = [
            ('site', Site),
            ('lieu_stockage', LieuStockage),
            ('localisation', Localisation),
            ('equipement', Equipement),
            ('piece', Piece),
            ('maintenance', Maintenance),
            ('user', User)
        ]
        
        for table_name, model in tables:
            csv_file = f'export_{table_name}.csv'
            
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    print(f"📊 Import {table_name}: {len(df)} enregistrements")
                    
                    for _, row in df.iterrows():
                        # Créer l'objet sans l'ID (sera auto-généré)
                        data = row.to_dict()
                        if 'id' in data:
                            del data['id']
                        
                        # Créer l'objet et l'ajouter
                        obj = model(**data)
                        db.session.add(obj)
                    
                    db.session.commit()
                    print(f"✅ {table_name}: Import réussi")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ Erreur import {table_name}: {e}")
            else:
                print(f"⚠️  Fichier {csv_file} non trouvé")
        
        print("🎉 Import terminé!")

def migrate_data():
    """Migration complète SQLite → PostgreSQL"""
    print("🔄 Migration SQLite → PostgreSQL")
    
    # Étape 1: Export
    export_sqlite_data()
    
    # Étape 2: Import
    import_to_postgresql()
    
    print("✅ Migration terminée!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'export':
            export_sqlite_data()
        elif command == 'import':
            import_to_postgresql()
        elif command == 'migrate':
            migrate_data()
        else:
            print("❌ Commande inconnue")
            print("Usage: python migrations.py [export|import|migrate]")
    else:
        print("🔄 Migration complète...")
        migrate_data() 