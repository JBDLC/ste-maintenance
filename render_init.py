#!/usr/bin/env python3
"""
Script d'initialisation pour Render
S'exécute automatiquement au démarrage pour créer les tables et données de base
"""

import os
from app import app, db, User, UserPermission
from werkzeug.security import generate_password_hash

def init_render_database():
    """Initialise la base de données PostgreSQL sur Render"""
    with app.app_context():
        try:
            # Créer toutes les tables
            print("🔧 Création des tables...")
            db.create_all()
            print("✅ Tables créées avec succès!")
            
            # Vérifier si l'utilisateur admin existe déjà
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("🔧 Création de l'utilisateur admin...")
                # Créer l'utilisateur admin
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                
                # Créer les permissions pour admin (toutes les permissions)
                pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
                         'maintenances', 'calendrier', 'mouvements', 'parametres']
                
                for page in pages:
                    permission = UserPermission(
                        user_id=admin_user.id,
                        page=page,
                        can_access=True
                    )
                    db.session.add(permission)
                
                db.session.commit()
                print("✅ Utilisateur admin créé avec toutes les permissions")
            else:
                print("✅ Utilisateur admin existe déjà")
            
            # Vérifier les permissions existantes
            permissions = UserPermission.query.filter_by(user_id=admin_user.id).all()
            existing_pages = [p.page for p in permissions]
            
            # Ajouter les permissions manquantes
            pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
                     'maintenances', 'calendrier', 'mouvements', 'parametres']
            
            for page in pages:
                if page not in existing_pages:
                    permission = UserPermission(
                        user_id=admin_user.id,
                        page=page,
                        can_access=True
                    )
                    db.session.add(permission)
                    print(f"➕ Permission ajoutée: {page}")
            
            db.session.commit()
            print("✅ Base de données PostgreSQL initialisée avec succès!")
            
            # Afficher les informations de connexion
            print(f"🔧 URI de base de données: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")
            raise

if __name__ == '__main__':
    init_render_database() 