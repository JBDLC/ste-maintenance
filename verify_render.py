#!/usr/bin/env python3
"""
Script de vérification pour Render
Vérifie que la base PostgreSQL fonctionne correctement
"""

import os
from app import app, db, User, UserPermission

def verify_render_setup():
    """Vérifie la configuration Render et PostgreSQL"""
    print("🔍 Vérification de la configuration Render...")
    
    # Vérifier les variables d'environnement
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL configurée: {database_url[:50]}...")
    else:
        print("❌ DATABASE_URL non configurée")
        return False
    
    with app.app_context():
        try:
            # Tester la connexion PostgreSQL
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Connexion PostgreSQL réussie!")
            
            # Vérifier les tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables disponibles: {', '.join(tables)}")
            
            # Vérifier l'utilisateur admin
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print("✅ Utilisateur admin trouvé")
                
                # Vérifier les permissions
                permissions = UserPermission.query.filter_by(user_id=admin_user.id).all()
                print(f"✅ {len(permissions)} permissions trouvées pour admin")
            else:
                print("⚠️ Utilisateur admin non trouvé - sera créé au démarrage")
            
            print("🎉 Configuration Render validée avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur de vérification: {e}")
            return False

if __name__ == '__main__':
    verify_render_setup() 