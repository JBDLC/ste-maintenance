#!/usr/bin/env python3
"""
Script de migration pour corriger la base PostgreSQL sur Render
"""

import os
import psycopg2
from sqlalchemy import create_engine, text

def fix_render_database():
    """Corriger la base PostgreSQL sur Render"""
    
    # Récupérer l'URL de la base depuis les variables d'environnement
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL non trouvée")
        return False
    
    try:
        # Créer une connexion directe PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 Vérification de la structure actuelle...")
        
        # Vérifier les colonnes existantes
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'maintenance';
        """)
        
        columns = [row[0] for row in cursor.fetchall()]
        print(f"📊 Colonnes existantes: {columns}")
        
        # Ajouter les nouveaux champs s'ils n'existent pas
        if 'equipement_nom_original' not in columns:
            print("🔧 Ajout du champ equipement_nom_original...")
            cursor.execute("""
                ALTER TABLE maintenance 
                ADD COLUMN equipement_nom_original VARCHAR(200);
            """)
        
        if 'localisation_nom_original' not in columns:
            print("🔧 Ajout du champ localisation_nom_original...")
            cursor.execute("""
                ALTER TABLE maintenance 
                ADD COLUMN localisation_nom_original VARCHAR(200);
            """)
        
        # Modifier equipement_id pour permettre NULL
        try:
            cursor.execute("""
                ALTER TABLE maintenance 
                ALTER COLUMN equipement_id DROP NOT NULL;
            """)
            print("✅ equipement_id peut maintenant être NULL")
        except Exception as e:
            print(f"⚠️ equipement_id peut déjà être NULL: {e}")
        
        # Vérifier la taille du champ titre
        cursor.execute("""
            SELECT character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'maintenance' AND column_name = 'titre';
        """)
        
        current_length = cursor.fetchone()[0]
        print(f"📊 Taille actuelle du champ titre: {current_length}")
        
        if current_length != 500:
            print("🔧 Modification de la taille du champ titre...")
            cursor.execute("""
                ALTER TABLE maintenance 
                ALTER COLUMN titre TYPE VARCHAR(500);
            """)
            print("✅ Titre modifié à 500 caractères")
        
        # Valider les changements
        conn.commit()
        
        # Vérifier la nouvelle structure
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'maintenance';
        """)
        
        new_columns = [row[0] for row in cursor.fetchall()]
        print(f"✅ Nouvelle structure: {new_columns}")
        
        cursor.close()
        conn.close()
        
        print("✅ Migration Render réussie !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration Render: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Début de la migration Render...")
    success = fix_render_database()
    if success:
        print("🎉 Migration terminée avec succès !")
    else:
        print("💥 Échec de la migration") 