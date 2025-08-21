#!/usr/bin/env python3
"""
Script de migration manuel PostgreSQL pour ajouter la colonne 'donnees_fournisseur'
Utilise SQLAlchemy avec la syntaxe text() pour compatibilité SQLAlchemy 2.0+
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def migrate():
    """Ajoute la colonne donnees_fournisseur à la table Piece sur PostgreSQL"""
    
    # Récupérer les variables d'environnement Render
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Variable d'environnement DATABASE_URL non trouvée")
        print("💡 Assurez-vous d'être sur Render ou de définir DATABASE_URL")
        return False
    
    try:
        # Connexion à la base PostgreSQL via SQLAlchemy
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print(f"🔗 Connexion établie à PostgreSQL")
        
        # Vérifier si la colonne existe déjà
        print("🔍 Vérification de l'existence de la colonne...")
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur'
        """)).fetchone()
        
        if result:
            print("✅ La colonne 'donnees_fournisseur' existe déjà")
            return True
        
        # Ajouter la colonne donnees_fournisseur
        print("🔧 Ajout de la colonne 'donnees_fournisseur'...")
        session.execute(text("""
            ALTER TABLE piece 
            ADD COLUMN donnees_fournisseur TEXT
        """))
        
        # Valider les changements
        session.commit()
        print("✅ Changements validés")
        
        # Vérifier que la colonne a été ajoutée
        result = session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur'
        """)).fetchone()
        
        if result:
            print(f"✅ Colonne ajoutée avec succès: {result[0]} ({result[1]})")
            return True
        else:
            print("❌ Erreur: La colonne n'a pas été ajoutée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'session' in locals():
            session.close()
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🚀 Migration PostgreSQL manuelle: Ajout de la colonne 'donnees_fournisseur'")
    print("=" * 70)
    
    success = migrate()
    
    if success:
        print("\n✅ Migration terminée avec succès!")
        print("🎉 Vous pouvez maintenant redémarrer l'application")
    else:
        print("\n❌ Migration échouée!")
        print("🔧 Vérifiez les logs et réessayez")
        sys.exit(1) 