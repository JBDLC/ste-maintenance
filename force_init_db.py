#!/usr/bin/env python3
"""
Script pour forcer l'initialisation de la base PostgreSQL sur Render
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"🔍 DATABASE_URL: {DATABASE_URL}")

if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
elif DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print(f"✅ URL configurée: {DATABASE_URL}")
else:
    print("❌ DATABASE_URL non trouvée!")
    exit(1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Définir tous les modèles
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=True)
    permissions = db.relationship('UserPermission', backref='user', lazy=True, cascade='all, delete-orphan')

class UserPermission(db.Model):
    __tablename__ = 'user_permission'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    page = db.Column(db.String(50), nullable=False)
    can_access = db.Column(db.Boolean, default=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'page', name='_user_page_uc'),)

class Site(db.Model):
    __tablename__ = 'site'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    localisations = db.relationship('Localisation', backref='site', lazy=True, cascade='all, delete-orphan')

class Localisation(db.Model):
    __tablename__ = 'localisation'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    equipements = db.relationship('Equipement', backref='localisation', lazy=True, cascade='all, delete-orphan')

class Equipement(db.Model):
    __tablename__ = 'equipement'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    localisation_id = db.Column(db.Integer, db.ForeignKey('localisation.id'), nullable=False)
    maintenances = db.relationship('Maintenance', backref='equipement', lazy=True, cascade='all, delete-orphan')
    pieces = db.relationship('PieceEquipement', backref='equipement', lazy=True, cascade='all, delete-orphan')

class Piece(db.Model):
    __tablename__ = 'piece'
    id = db.Column(db.Integer, primary_key=True)
    reference_ste = db.Column(db.String(50), nullable=True)
    reference_magasin = db.Column(db.String(50))
    item = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text)
    lieu_stockage_id = db.Column(db.Integer, db.ForeignKey('lieu_stockage.id'), nullable=True)
    quantite_stock = db.Column(db.Integer, default=0)
    stock_mini = db.Column(db.Integer, default=0)
    stock_maxi = db.Column(db.Integer, default=0)
    mouvements = db.relationship('MouvementPiece', backref='piece', lazy=True)
    equipements = db.relationship('PieceEquipement', backref='piece', lazy=True)

class PieceEquipement(db.Model):
    __tablename__ = 'piece_equipement'
    id = db.Column(db.Integer, primary_key=True)
    equipement_id = db.Column(db.Integer, db.ForeignKey('equipement.id'), nullable=False)
    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'), nullable=False)

class Maintenance(db.Model):
    __tablename__ = 'maintenance'
    id = db.Column(db.Integer, primary_key=True)
    equipement_id = db.Column(db.Integer, db.ForeignKey('equipement.id'), nullable=False)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    periodicite = db.Column(db.String(20), nullable=False)  # semaine, 2_semaines, mois, 2_mois, 4_mois, 6_mois, 1_an, 2_ans
    date_premiere = db.Column(db.Date, nullable=True)
    date_prochaine = db.Column(db.Date, nullable=True)
    active = db.Column(db.Boolean, default=True)
    date_importee = db.Column(db.Boolean, default=False)
    interventions = db.relationship('Intervention', backref='maintenance', lazy=True, cascade='all, delete-orphan')

class Intervention(db.Model):
    __tablename__ = 'intervention'
    id = db.Column(db.Integer, primary_key=True)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=False)
    date_planifiee = db.Column(db.Date, nullable=False)
    date_realisee = db.Column(db.Date)
    statut = db.Column(db.String(20), default='planifiee')
    commentaire = db.Column(db.Text)
    pieces_utilisees = db.relationship('PieceUtilisee', backref='intervention', lazy=True, cascade='all, delete-orphan')

class PieceUtilisee(db.Model):
    __tablename__ = 'piece_utilisee'
    id = db.Column(db.Integer, primary_key=True)
    intervention_id = db.Column(db.Integer, db.ForeignKey('intervention.id'), nullable=False)
    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'), nullable=False)
    quantite = db.Column(db.Integer, default=1)
    piece = db.relationship('Piece')

class LieuStockage(db.Model):
    __tablename__ = 'lieu_stockage'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    pieces = db.relationship('Piece', backref='lieu_stockage', lazy=True)

class MouvementPiece(db.Model):
    __tablename__ = 'mouvement_piece'
    id = db.Column(db.Integer, primary_key=True)
    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'), nullable=False)
    type_mouvement = db.Column(db.String(20), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=db.func.now())
    motif = db.Column(db.String(100))
    intervention_id = db.Column(db.Integer, db.ForeignKey('intervention.id'), nullable=True)
    intervention = db.relationship('Intervention')

class Parametre(db.Model):
    __tablename__ = 'parametre'
    id = db.Column(db.Integer, primary_key=True)
    cle = db.Column(db.String(100), unique=True, nullable=False)
    valeur = db.Column(db.String(255), nullable=False)

def force_init_database():
    """Force l'initialisation de la base de données"""
    try:
        with app.app_context():
            print("🔍 Suppression de toutes les tables existantes...")
            db.drop_all()
            print("✅ Tables supprimées")
            
            print("🔍 Création de toutes les tables...")
            db.create_all()
            print("✅ Tables créées avec succès!")
            
            # Créer un utilisateur admin
            print("🔍 Création de l'utilisateur admin...")
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin créé avec ID: {admin.id}")
            
            # Créer les permissions pour l'admin
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
            print("✅ Permissions créées avec succès!")
            
            # Vérifier que l'admin existe
            admin_check = User.query.filter_by(username='admin').first()
            if admin_check:
                print(f"✅ Vérification: Admin trouvé avec ID {admin_check.id}")
            else:
                print("❌ ERREUR: Admin non trouvé après création!")
            
            print("🎉 Initialisation forcée terminée avec succès!")
            print("📋 Identifiants de connexion:")
            print("   Username: admin")
            print("   Password: admin123")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation forcée: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    force_init_database() 