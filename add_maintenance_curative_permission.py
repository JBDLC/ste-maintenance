#!/usr/bin/env python3
"""
Script pour ajouter la permission maintenance_curative à l'utilisateur admin
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire courant au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, UserPermission

def add_maintenance_curative_permission():
    """Ajoute la permission maintenance_curative à l'utilisateur admin"""
    
    with app.app_context():
        try:
            print("🔧 Ajout de la permission maintenance_curative...")
            
            # Récupérer l'utilisateur admin (ID 1)
            admin_user_id = 1
            
            # Vérifier si la permission existe déjà
            existing_permission = UserPermission.query.filter_by(
                user_id=admin_user_id, 
                page='maintenance_curative'
            ).first()
            
            if existing_permission:
                print("✅ Permission maintenance_curative existe déjà pour l'admin")
                existing_permission.can_access = True
            else:
                print("➕ Création de la permission maintenance_curative pour l'admin")
                new_permission = UserPermission(
                    user_id=admin_user_id,
                    page='maintenance_curative',
                    can_access=True
                )
                db.session.add(new_permission)
            
            db.session.commit()
            print("✅ Permission ajoutée avec succès!")
            
            # Vérifier toutes les permissions de l'admin
            admin_permissions = UserPermission.query.filter_by(user_id=admin_user_id).all()
            print(f"\n📋 Permissions actuelles de l'admin:")
            for perm in admin_permissions:
                status = "✅ Activée" if perm.can_access else "❌ Désactivée"
                print(f"  - {perm.page}: {status}")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de la permission: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Ajout de la permission maintenance_curative...")
    
    if add_maintenance_curative_permission():
        print("\n🎉 Permission ajoutée avec succès!")
        print("Vous pouvez maintenant accéder à la page Maintenance Curative.")
    else:
        print("\n💥 Échec de l'ajout de la permission!")
        sys.exit(1) 