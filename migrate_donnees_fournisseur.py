#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne 'donnees_fournisseur' à la table Piece
"""

import sqlite3
import os

def migrate():
    """Ajoute la colonne donnees_fournisseur à la table Piece"""
    
    # Chemin vers la base de données
    db_path = os.path.join('instance', 'maintenance.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(Piece)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'donnees_fournisseur' in columns:
            print("✅ La colonne 'donnees_fournisseur' existe déjà")
            return True
        
        # Ajouter la colonne donnees_fournisseur
        print("🔧 Ajout de la colonne 'donnees_fournisseur'...")
        cursor.execute("""
            ALTER TABLE Piece 
            ADD COLUMN donnees_fournisseur TEXT
        """)
        
        # Valider les changements
        conn.commit()
        
        # Vérifier que la colonne a été ajoutée
        cursor.execute("PRAGMA table_info(Piece)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'donnees_fournisseur' in columns:
            print("✅ Colonne 'donnees_fournisseur' ajoutée avec succès!")
            return True
        else:
            print("❌ Erreur: La colonne n'a pas été ajoutée")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Migration: Ajout de la colonne 'donnees_fournisseur'")
    print("=" * 50)
    
    success = migrate()
    
    if success:
        print("\n✅ Migration terminée avec succès!")
    else:
        print("\n❌ Migration échouée!")
        exit(1) 