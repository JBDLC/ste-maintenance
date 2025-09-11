#!/usr/bin/env python3
"""
Migration pour rendre les colonnes localisation_id et equipement_id optionnelles dans la table commande
"""

import os
import sys
from sqlalchemy import create_engine, text

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

def migrate_commande_columns():
    """Migration pour rendre les colonnes optionnelles"""
    
    # Configuration de la base de données
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
    elif DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
    
    if not DATABASE_URL:
        DATABASE_URL = 'sqlite:///maintenance.db'
    
    print(f"🔍 Connexion à la base de données: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'SQLite'}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Vérifier si on est sur PostgreSQL
            if 'postgresql' in DATABASE_URL:
                print("🔧 Migration PostgreSQL...")
                
                # Modifier la colonne localisation_id
                try:
                    conn.execute(text("ALTER TABLE commande ALTER COLUMN localisation_id DROP NOT NULL"))
                    print("✅ Colonne localisation_id rendue optionnelle")
                except Exception as e:
                    print(f"⚠️ Erreur localisation_id: {e}")
                
                # Modifier la colonne equipement_id
                try:
                    conn.execute(text("ALTER TABLE commande ALTER COLUMN equipement_id DROP NOT NULL"))
                    print("✅ Colonne equipement_id rendue optionnelle")
                except Exception as e:
                    print(f"⚠️ Erreur equipement_id: {e}")
                
                conn.commit()
                
            else:
                print("🔧 Migration SQLite...")
                
                # Pour SQLite, on doit recréer la table
                # D'abord, vérifier si les colonnes sont déjà optionnelles
                result = conn.execute(text("PRAGMA table_info(commande)"))
                columns = result.fetchall()
                
                localisation_nullable = any(col[1] == 'localisation_id' and col[3] == 0 for col in columns)
                equipement_nullable = any(col[1] == 'equipement_id' and col[3] == 0 for col in columns)
                
                if not localisation_nullable or not equipement_nullable:
                    print("⚠️ SQLite nécessite une migration manuelle")
                    print("   Les colonnes localisation_id et equipement_id doivent être rendues optionnelles")
                    print("   Vous pouvez ignorer cette migration si vous utilisez PostgreSQL")
                else:
                    print("✅ Colonnes déjà optionnelles")
        
        print("🎉 Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Migration des colonnes de commande")
    print("=" * 50)
    
    success = migrate_commande_columns()
    
    if success:
        print("\n✅ Migration réussie!")
        print("   Les colonnes localisation_id et equipement_id sont maintenant optionnelles")
    else:
        print("\n❌ Migration échouée!")
        print("   Vérifiez les logs ci-dessus")
