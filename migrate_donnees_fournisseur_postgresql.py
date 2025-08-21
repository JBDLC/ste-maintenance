#!/usr/bin/env python3
"""
Script de migration PostgreSQL pour ajouter la colonne 'donnees_fournisseur' à la table Piece
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def migrate():
    """Ajoute la colonne donnees_fournisseur à la table Piece sur PostgreSQL"""
    
    # Récupérer les variables d'environnement Render
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Variable d'environnement DATABASE_URL non trouvée")
        return False
    
    try:
        # Connexion à la base PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur'
        """)
        
        if cursor.fetchone():
            print("✅ La colonne 'donnees_fournisseur' existe déjà")
            return True
        
        # Ajouter la colonne donnees_fournisseur
        print("🔧 Ajout de la colonne 'donnees_fournisseur'...")
        cursor.execute("""
            ALTER TABLE piece 
            ADD COLUMN donnees_fournisseur TEXT
        """)
        
        # Vérifier que la colonne a été ajoutée
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur'
        """)
        
        if cursor.fetchone():
            print("✅ Colonne 'donnees_fournisseur' ajoutée avec succès!")
            return True
        else:
            print("❌ Erreur: La colonne n'a pas été ajoutée")
            return False
            
    except psycopg2.Error as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Migration PostgreSQL: Ajout de la colonne 'donnees_fournisseur'")
    print("=" * 60)
    
    success = migrate()
    
    if success:
        print("\n✅ Migration terminée avec succès!")
    else:
        print("\n❌ Migration échouée!")
        exit(1) 