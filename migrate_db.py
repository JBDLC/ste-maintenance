#!/usr/bin/env python3
"""
Script de migration pour ajouter les nouveaux champs à la base de données existante
Usage: python migrate_db.py
"""

import os
import sqlite3
from dotenv import load_dotenv
from app import app, db

load_dotenv()

def migrate_database():
    """Migre la base de données existante avec les nouveaux champs"""
    with app.app_context():
        print("🔄 Migration de la base de données...")
        
        # Vérifier si la base existe
        db_path = 'maintenance.db'
        if not os.path.exists(db_path):
            print("❌ Base de données non trouvée. Création d'une nouvelle base...")
            db.create_all()
            print("✅ Nouvelle base de données créée!")
            return
        
        # Connexion directe à SQLite pour les modifications
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Vérifier si la colonne 'active' existe dans la table user
            cursor.execute("PRAGMA table_info(user)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'active' not in columns:
                print("➕ Ajout de la colonne 'active' à la table user...")
                cursor.execute("ALTER TABLE user ADD COLUMN active BOOLEAN DEFAULT 1")
                print("✅ Colonne 'active' ajoutée!")
            
            # Vérifier si la table user_permission existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_permission'")
            if not cursor.fetchone():
                print("➕ Création de la table user_permission...")
                cursor.execute("""
                    CREATE TABLE user_permission (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        page VARCHAR(50) NOT NULL,
                        can_view BOOLEAN DEFAULT 0,
                        can_create BOOLEAN DEFAULT 0,
                        can_edit BOOLEAN DEFAULT 0,
                        can_delete BOOLEAN DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES user (id),
                        UNIQUE(user_id, page)
                    )
                """)
                print("✅ Table user_permission créée!")
            
            # Vérifier si la contrainte unique existe
            cursor.execute("PRAGMA index_list(user_permission)")
            indexes = [index[1] for index in cursor.fetchall()]
            
            if '_user_page_uc' not in indexes:
                print("➕ Ajout de la contrainte unique...")
                cursor.execute("CREATE UNIQUE INDEX _user_page_uc ON user_permission (user_id, page)")
                print("✅ Contrainte unique ajoutée!")
            
            conn.commit()
            print("✅ Migration terminée avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {e}")
            conn.rollback()
        finally:
            conn.close()

def create_default_permissions():
    """Crée les permissions par défaut pour les utilisateurs existants"""
    with app.app_context():
        from app import User, UserPermission, create_user_permissions
        
        print("🔧 Création des permissions par défaut...")
        
        # Récupérer tous les utilisateurs
        users = User.query.all()
        
        for user in users:
            # Vérifier si l'utilisateur a déjà des permissions
            existing_permissions = UserPermission.query.filter_by(user_id=user.id).count()
            
            if existing_permissions == 0:
                print(f"➕ Création des permissions pour {user.username}...")
                create_user_permissions(user.id)
                print(f"✅ Permissions créées pour {user.username}")
            else:
                print(f"ℹ️  {user.username} a déjà des permissions")
        
        print("✅ Permissions par défaut créées!")

if __name__ == '__main__':
    print("🚀 Début de la migration...")
    migrate_database()
    create_default_permissions()
    print("🎉 Migration complète terminée!") 