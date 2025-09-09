#!/usr/bin/env python3
"""
Script de migration manuel pour Render - Ajouter la colonne piece_id
À exécuter directement sur Render si la migration automatique échoue
"""

import os
import sys
from sqlalchemy import create_engine, text

def migrate_render_manual():
    """Migration manuelle pour Render"""
    
    # Configuration de la base de données PostgreSQL sur Render
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ Variable d'environnement DATABASE_URL non trouvée")
        sys.exit(1)
    
    # Corriger l'URL pour psycopg
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
    elif DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
    
    try:
        print("🔧 Migration manuelle Render - Ajout de la colonne piece_id...")
        print(f"🔧 URL de base de données: {DATABASE_URL[:50]}...")
        
        # Créer l'engine de base de données
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'commande' AND column_name = 'piece_id'
            """))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                print("❌ Colonne piece_id manquante - ajout en cours...")
                
                # Ajouter la colonne piece_id
                conn.execute(text("""
                    ALTER TABLE commande 
                    ADD COLUMN piece_id INTEGER REFERENCES piece(id)
                """))
                conn.commit()
                print("✅ Colonne piece_id ajoutée à la table commande")
            else:
                print("ℹ️ La colonne piece_id existe déjà")
        
        print("✅ Migration manuelle terminée avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration manuelle: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    migrate_render_manual()

