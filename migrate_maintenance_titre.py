#!/usr/bin/env python3
"""
Script de migration pour augmenter la taille du champ titre dans la table maintenance
"""

import os
import sys
from sqlalchemy import create_engine, text

def migrate_maintenance_titre():
    """Migration pour augmenter la taille du champ titre de 100 à 500 caractères"""
    
    # Configuration de la base de données
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
    elif DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL non définie")
        return False
    
    try:
        # Créer l'engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Vérifier si la table existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'maintenance'
                );
            """))
            
            if not result.scalar():
                print("❌ Table 'maintenance' n'existe pas")
                return False
            
            # Vérifier la taille actuelle du champ titre
            result = conn.execute(text("""
                SELECT character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'maintenance' AND column_name = 'titre';
            """))
            
            current_length = result.scalar()
            print(f"📊 Taille actuelle du champ titre: {current_length}")
            
            if current_length == 500:
                print("✅ Le champ titre est déjà à la bonne taille (500)")
                return True
            
            # Modifier la taille du champ
            print("🔧 Modification de la taille du champ titre...")
            conn.execute(text("""
                ALTER TABLE maintenance 
                ALTER COLUMN titre TYPE VARCHAR(500);
            """))
            
            conn.commit()
            print("✅ Migration réussie ! Le champ titre peut maintenant contenir jusqu'à 500 caractères")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Migration du champ titre de la table maintenance...")
    success = migrate_maintenance_titre()
    if success:
        print("✅ Migration terminée avec succès")
        sys.exit(0)
    else:
        print("❌ Migration échouée")
        sys.exit(1) 