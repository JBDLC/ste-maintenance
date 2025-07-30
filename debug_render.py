#!/usr/bin/env python3
"""
Script de diagnostic pour Render avec PostgreSQL
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"🔍 DATABASE_URL: {DATABASE_URL}")

if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg2://', 1)
elif DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://', 1)

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print(f"✅ URL configurée: {DATABASE_URL}")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maintenance.db'
    print("⚠️ Utilisation de SQLite (pas de DATABASE_URL)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def test_database_connection():
    """Test de connexion à la base de données"""
    try:
        print("🔍 Test de connexion à la base de données...")
        with app.app_context():
            # Test simple de connexion
            db.engine.execute("SELECT 1")
            print("✅ Connexion à PostgreSQL réussie!")
            
            # Vérifier les tables
            result = db.engine.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in result]
            print(f"📋 Tables trouvées: {tables}")
            
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_models():
    """Test de création des modèles"""
    try:
        print("🔍 Test de création des modèles...")
        with app.app_context():
            # Créer les tables
            db.create_all()
            print("✅ Tables créées avec succès!")
            return True
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return False

def test_user_creation():
    """Test de création d'un utilisateur admin"""
    try:
        print("🔍 Test de création d'utilisateur admin...")
        with app.app_context():
            from werkzeug.security import generate_password_hash
            
            # Importer les modèles
            from app import User, UserPermission
            
            # Vérifier si l'admin existe déjà
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("✅ Utilisateur admin existe déjà")
                return True
            
            # Créer l'admin
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            
            # Créer les permissions
            pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
                     'maintenances', 'calendrier', 'mouvements', 'parametres']
            
            for page in pages:
                permission = UserPermission(
                    user_id=admin.id,
                    page=page,
                    can_access=True
                )
                db.session.add(permission)
            
            db.session.commit()
            print("✅ Utilisateur admin créé avec succès!")
            return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")
        return False

def main():
    print("🚀 Diagnostic de l'application sur Render")
    print("=" * 50)
    
    # Test 1: Connexion à la base
    if not test_database_connection():
        print("❌ ÉCHEC: Impossible de se connecter à PostgreSQL")
        return
    
    # Test 2: Création des tables
    if not test_models():
        print("❌ ÉCHEC: Impossible de créer les tables")
        return
    
    # Test 3: Création de l'admin
    if not test_user_creation():
        print("❌ ÉCHEC: Impossible de créer l'utilisateur admin")
        return
    
    print("✅ TOUS LES TESTS RÉUSSIS!")
    print("🎉 L'application devrait fonctionner correctement")

if __name__ == "__main__":
    main() 