#!/usr/bin/env python3
"""
Script de migration pour corriger la longueur du champ titre sur Render
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configuration pour Render
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL non trouvée")
    sys.exit(1)

# Convertir l'URL PostgreSQL de Render
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"🔗 Connexion à la base de données Render...")

def migrate_titre_length():
    """Migre le champ titre de VARCHAR(100) à VARCHAR(200)"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔧 Vérification de la structure actuelle...")
            
            # Vérifier la structure actuelle
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'maintenance' AND column_name = 'titre'
            """))
            
            current_structure = result.fetchone()
            if current_structure:
                print(f"📊 Structure actuelle : {current_structure[1]}({current_structure[2]})")
                
                if current_structure[2] == 100:
                    print("🔧 Application de la migration...")
                    conn.execute(text("""
                        ALTER TABLE maintenance 
                        ALTER COLUMN titre TYPE VARCHAR(200)
                    """))
                    conn.commit()
                    print("✅ Migration réussie ! titre est maintenant VARCHAR(200)")
                else:
                    print(f"✅ Déjà migré : titre est {current_structure[1]}({current_structure[2]})")
            else:
                print("❌ Table maintenance ou colonne titre non trouvée")
                return False
                
    except SQLAlchemyError as e:
        print(f"❌ Erreur SQL : {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Migration du champ titre pour Render...")
    success = migrate_titre_length()
    
    if success:
        print("\n🎉 Migration terminée ! Vous pouvez maintenant importer vos maintenances.")
    else:
        print("\n❌ Migration échouée.")
        sys.exit(1) 