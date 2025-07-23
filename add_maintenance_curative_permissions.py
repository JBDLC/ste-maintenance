#!/usr/bin/env python3
"""
Script pour ajouter la permission maintenance_curative à tous les utilisateurs existants
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire courant au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, UserPermission

def add_maintenance_curative_permissions():
    """Ajoute la permission maintenance_curative à tous les utilisateurs existants"""
    
    with app.app_context():
        try:
            print("🔧 Ajout de la permission maintenance_curative à tous les utilisateurs...")
            
            # Récupérer tous les utilisateurs actifs
            users = User.query.filter_by(active=True).all()
            print(f"📋 {len(users)} utilisateurs trouvés")
            
            permissions_added = 0
            permissions_updated = 0
            
            for user in users:
                # Vérifier si la permission existe déjà
                existing_permission = UserPermission.query.filter_by(
                    user_id=user.id, 
                    page='maintenance_curative'
                ).first()
                
                if existing_permission:
                    print(f"✅ Permission maintenance_curative existe déjà pour {user.username}")
                    permissions_updated += 1
                else:
                    print(f"➕ Création de la permission maintenance_curative pour {user.username}")
                    new_permission = UserPermission(
                        user_id=user.id,
                        page='maintenance_curative',
                        can_access=False  # Par défaut, pas d'accès
                    )
                    db.session.add(new_permission)
                    permissions_added += 1
            
            db.session.commit()
            print(f"✅ {permissions_added} nouvelles permissions ajoutées")
            print(f"✅ {permissions_updated} permissions existantes vérifiées")
            
            # Afficher un résumé des permissions pour chaque utilisateur
            print(f"\n📋 Résumé des permissions:")
            for user in users:
                permissions = UserPermission.query.filter_by(user_id=user.id).all()
                print(f"  - {user.username}: {len(permissions)} permissions")
                for perm in permissions:
                    status = "✅ Activée" if perm.can_access else "❌ Désactivée"
                    print(f"    • {perm.page}: {status}")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout des permissions: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Ajout de la permission maintenance_curative...")
    
    if add_maintenance_curative_permissions():
        print("\n🎉 Permissions ajoutées avec succès!")
        print("Vous pouvez maintenant gérer les permissions dans l'interface utilisateur.")
    else:
        print("\n💥 Échec de l'ajout des permissions!")
        sys.exit(1) 