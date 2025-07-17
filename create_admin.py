#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur par défaut
Usage: python create_admin.py
"""

import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from app import app, db, User, UserPermission

load_dotenv()

def create_admin_user():
    """Crée un utilisateur administrateur avec tous les droits"""
    with app.app_context():
        # Vérifier si l'admin existe déjà
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("❌ L'utilisateur admin existe déjà")
            return
        
        # Créer l'utilisateur admin
        admin = User(
            username='admin',
            email='admin@maintenance-ste.com',
            password_hash=generate_password_hash('admin123'),
            active=True
        )
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Utilisateur admin créé avec succès!")
        print("📧 Email: admin@maintenance-ste.com")
        print("🔑 Mot de passe: admin123")
        print("⚠️  N'oubliez pas de changer le mot de passe!")
        
        # Créer toutes les permissions (tous les droits)
        pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
                 'maintenances', 'calendrier', 'mouvements', 'parametres']
        
        for page in pages:
            permission = UserPermission(
                user_id=admin.id,
                page=page,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True
            )
            db.session.add(permission)
        
        db.session.commit()
        print("✅ Permissions administrateur créées avec succès!")

if __name__ == '__main__':
    print("🔧 Création de l'utilisateur administrateur...")
    create_admin_user() 