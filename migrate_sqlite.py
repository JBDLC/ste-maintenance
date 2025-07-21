#!/usr/bin/env python3
"""
Script de migration pour SQLite - Ajoute les nouveaux champs à la table maintenance
"""

import sqlite3
import os

def migrate_sqlite_database():
    """Migration de la base SQLite pour ajouter les nouveaux champs"""
    
    # Chemin vers la base SQLite
    db_path = 'maintenance.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données {db_path} non trouvée")
        return False
    
    try:
        # Connexion à la base SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Vérification de la structure actuelle...")
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(maintenance)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📊 Colonnes existantes: {columns}")
        
        # Vérifier la taille du champ titre
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='maintenance'")
        table_sql = cursor.fetchone()[0]
        print(f"📋 Structure actuelle: {table_sql}")
        
        # Ajouter les nouveaux champs s'ils n'existent pas
        if 'equipement_nom_original' not in columns:
            print("🔧 Ajout du champ equipement_nom_original...")
            cursor.execute("ALTER TABLE maintenance ADD COLUMN equipement_nom_original TEXT")
        
        if 'localisation_nom_original' not in columns:
            print("🔧 Ajout du champ localisation_nom_original...")
            cursor.execute("ALTER TABLE maintenance ADD COLUMN localisation_nom_original TEXT")
        
        # Modifier equipement_id pour permettre NULL (SQLite le permet par défaut)
        print("✅ equipement_id peut déjà être NULL en SQLite")
        
        # Valider les changements
        conn.commit()
        
        # Vérifier la nouvelle structure
        cursor.execute("PRAGMA table_info(maintenance)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"✅ Nouvelle structure: {new_columns}")
        
        conn.close()
        print("✅ Migration SQLite réussie !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration SQLite: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Début de la migration SQLite...")
    success = migrate_sqlite_database()
    if success:
        print("🎉 Migration terminée avec succès !")
    else:
        print("💥 Échec de la migration") 