#!/usr/bin/env python3
"""
Script pour augmenter la longueur du champ titre de la table maintenance
de 100 à 200 caractères pour éviter les erreurs d'import
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configuration de la base de données PostgreSQL de Render
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ Variable d'environnement DATABASE_URL non trouvée")
    print("💡 Assurez-vous d'être connecté à votre base de données Render")
    sys.exit(1)

# Convertir l'URL PostgreSQL de Render
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"🔗 Connexion à la base de données : {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Base locale'}")

def fix_titre_length():
    """Augmente la longueur du champ titre de 100 à 200 caractères"""
    try:
        # Créer la connexion
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔧 Modification de la longueur du champ titre...")
            
            # PostgreSQL - modifier directement la colonne
            conn.execute(text("""
                ALTER TABLE maintenance 
                ALTER COLUMN titre TYPE VARCHAR(200)
            """))
            print("✅ PostgreSQL : Champ titre modifié à VARCHAR(200)")
            
            conn.commit()
            print("✅ Migration terminée avec succès !")
            
    except SQLAlchemyError as e:
        print(f"❌ Erreur lors de la migration : {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Début de la migration pour corriger la longueur du titre...")
    success = fix_titre_length()
    
    if success:
        print("\n🎉 Migration réussie ! Vous pouvez maintenant importer vos maintenances.")
        print("💡 Le champ titre accepte maintenant jusqu'à 200 caractères.")
    else:
        print("\n❌ Migration échouée. Vérifiez les logs ci-dessus.")
        sys.exit(1) 