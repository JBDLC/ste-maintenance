from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fpdf import FPDF
import io
import csv
import json
import tempfile
import csv
from sqlalchemy.inspection import inspect
from dateutil.parser import parse as parse_date
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Fonctions utilitaires pour remplacer pandas
def create_dataframe(data, columns=None):
    """Crée une structure de données similaire à un DataFrame pandas"""
    if not data:
        return {'data': [], 'columns': columns or []}
    if columns is None:
        columns = list(data[0].keys()) if data else []
    return {'data': data, 'columns': columns}

def is_na(value):
    """Vérifie si une valeur est NaN (équivalent à pd.isna)"""
    return value is None or (isinstance(value, float) and str(value).lower() == 'nan')

def read_excel_simple(file_path, sheet_name=None):
    """Lit un fichier Excel de manière simple (remplace pd.read_excel)"""
    try:
        from openpyxl import load_workbook
        wb = load_workbook(file_path, data_only=True)
        
        if sheet_name:
            ws = wb[sheet_name]
        else:
            ws = wb.active
            
        data = []
        for row in ws.iter_rows(values_only=True):
            if any(cell is not None for cell in row):
                data.append(list(row))
        
        if not data:
            return {'data': [], 'columns': []}
            
        # Première ligne comme en-têtes
        headers = data[0]
        rows = data[1:]
        
        # Convertir en liste de dictionnaires
        result = []
        for row in rows:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = row[i]
                else:
                    row_dict[header] = None
            result.append(row_dict)
            
        return {'data': result, 'columns': headers}
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier Excel: {e}")
        return {'data': [], 'columns': []}

def write_excel_simple(data, file_path, sheet_name='Sheet1'):
    """Écrit des données dans un fichier Excel (remplace pd.ExcelWriter)"""
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        if not data:
            wb.save(file_path)
            return
            
        # Écrire les en-têtes
        if data and len(data) > 0:
            headers = list(data[0].keys())
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            
            # Écrire les données
            for row_idx, row_data in enumerate(data, 2):
                for col_idx, header in enumerate(headers, 1):
                    ws.cell(row=row_idx, column=col_idx, value=row_data.get(header))
        
        wb.save(file_path)
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier Excel: {e}")

def read_csv_simple(content):
    """Lit du contenu CSV (remplace pd.read_csv)"""
    try:
        if isinstance(content, str):
            content = io.StringIO(content)
        
        reader = csv.DictReader(content)
        data = list(reader)
        columns = reader.fieldnames or []
        
        return {'data': data, 'columns': columns}
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV: {e}")
        return {'data': [], 'columns': []}

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
elif DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maintenance.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration email
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modèles de données
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=True)
    permissions = db.relationship('UserPermission', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Définit le mot de passe hashé"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash"""
        return check_password_hash(self.password_hash, password)

class UserPermission(db.Model):
    __tablename__ = 'user_permission'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    page = db.Column(db.String(50), nullable=False)  # sites, localisations, equipements, etc.
    can_access = db.Column(db.Boolean, default=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'page', name='_user_page_uc'),)

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    localisations = db.relationship('Localisation', backref='site', lazy=True, cascade='all, delete-orphan')

class Localisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    equipements = db.relationship('Equipement', backref='localisation', lazy=True, cascade='all, delete-orphan')

class Equipement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    localisation_id = db.Column(db.Integer, db.ForeignKey('localisation.id'), nullable=False)
    maintenances = db.relationship('Maintenance', backref='equipement', lazy=True, cascade='all, delete-orphan')
    pieces = db.relationship('PieceEquipement', backref='equipement', lazy=True, cascade='all, delete-orphan')

class Piece(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    equipement_id = db.Column(db.Integer, db.ForeignKey('equipement.id'), nullable=False)
    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'), nullable=False)

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipement_id = db.Column(db.Integer, db.ForeignKey('equipement.id'), nullable=False)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    periodicite = db.Column(db.String(20), nullable=False)  # semaine, 2_semaines, mois, 2_mois, 6_mois, 1_an, 2_ans
    date_premiere = db.Column(db.Date, nullable=True)  # Peut être NULL pour les maintenances importées
    date_prochaine = db.Column(db.Date, nullable=True)  # Peut être NULL pour les maintenances importées
    active = db.Column(db.Boolean, default=True)
    date_importee = db.Column(db.Boolean, default=False)  # Marque les maintenances importées sans date
    interventions = db.relationship('Intervention', backref='maintenance', lazy=True, cascade='all, delete-orphan')

class Intervention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=False)
    date_planifiee = db.Column(db.Date, nullable=False)
    date_realisee = db.Column(db.Date)
    statut = db.Column(db.String(20), default='planifiee')  # planifiee, realisee, annulee
    commentaire = db.Column(db.Text)
    pieces_utilisees = db.relationship('PieceUtilisee', backref='intervention', lazy=True, cascade='all, delete-orphan')

class PieceUtilisee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intervention_id = db.Column(db.Integer, db.ForeignKey('intervention.id'), nullable=False)
    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'), nullable=False)
    quantite = db.Column(db.Integer, default=1)
    piece = db.relationship('Piece')

class LieuStockage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    pieces = db.relationship('Piece', backref='lieu_stockage', lazy=True)

class MouvementPiece(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'), nullable=False)
    type_mouvement = db.Column(db.String(20), nullable=False)  # entree, sortie
    quantite = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    motif = db.Column(db.String(100))
    intervention_id = db.Column(db.Integer, db.ForeignKey('intervention.id'), nullable=True)
    intervention = db.relationship('Intervention')

class Parametre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cle = db.Column(db.String(100), unique=True, nullable=False)
    valeur = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Fonctions de gestion des permissions
def get_user_permissions(user_id):
    """Récupère toutes les permissions d'un utilisateur"""
    permissions = UserPermission.query.filter_by(user_id=user_id).all()
    return {p.page: p for p in permissions}

def has_permission(user_id, page, action='view'):
    """Vérifie si un utilisateur a une permission spécifique"""
    if not user_id:
        return False
    
    permission = UserPermission.query.filter_by(user_id=user_id, page=page).first()
    if not permission:
        return False
    
    if action == 'view':
        return permission.can_access
    elif action == 'create':
        return permission.can_access
    elif action == 'edit':
        return permission.can_access
    elif action == 'delete':
        return permission.can_access
    return False

def create_user_permissions(user_id):
    """Crée les permissions par défaut (aucune) pour un nouvel utilisateur"""
    pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
             'maintenances', 'calendrier', 'mouvements', 'parametres']
    
    for page in pages:
        permission = UserPermission(
            user_id=user_id,
            page=page,
            can_access=False
        )
        db.session.add(permission)
    
    db.session.commit()

def update_user_permissions(user_id, permissions_data):
    """Met à jour les permissions d'un utilisateur"""
    for page, actions in permissions_data.items():
        permission = UserPermission.query.filter_by(user_id=user_id, page=page).first()
        if permission:
            permission.can_access = actions.get('access', False)
    
    db.session.commit()

# Rendre la fonction has_permission accessible dans les templates
@app.context_processor
def inject_permissions():
    """Injecte la fonction has_permission dans le contexte des templates"""
    return dict(has_permission=has_permission)

# Routes principales
@app.route('/')
@login_required
def index():
    # Récupérer les données pour le tableau de bord
    sites = Site.query.all()
    equipements = Equipement.query.all()
    maintenances = Maintenance.query.all()
    pieces = Piece.query.all()
    
    # Interventions de la semaine (corrigé pour semaine calendaire)
    today = datetime.now().date()
    lundi = today - timedelta(days=today.weekday())
    dimanche = lundi + timedelta(days=6)
    interventions_semaine = Intervention.query.filter(
        Intervention.date_planifiee >= lundi,
        Intervention.date_planifiee <= dimanche
    ).all()
    
    # Pièces en rupture
    pieces_rupture = Piece.query.filter(Piece.quantite_stock <= Piece.stock_mini).all()
    
    return render_template('index.html', 
                         sites=sites, 
                         equipements=equipements, 
                         maintenances=maintenances, 
                         pieces=pieces,
                         interventions_semaine=interventions_semaine,
                         pieces_rupture=pieces_rupture)

@app.route('/sites')
@login_required
def sites():
    sites_list = Site.query.all()
    return render_template('sites.html', sites=sites_list)

@app.route('/site/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_site():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        site = Site(nom=nom, description=description)
        db.session.add(site)
        db.session.commit()
        flash('Site ajouté avec succès!', 'success')
        return redirect(url_for('sites'))
    return render_template('ajouter_site.html')

@app.route('/localisations')
@login_required
def localisations():
    localisations_list = Localisation.query.all()
    return render_template('localisations.html', localisations=localisations_list)

@app.route('/localisation/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_localisation():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        site_id = request.form['site_id']
        localisation = Localisation(nom=nom, description=description, site_id=site_id)
        db.session.add(localisation)
        db.session.commit()
        flash('Localisation ajoutée avec succès!', 'success')
        return redirect(url_for('localisations'))
    sites = Site.query.all()
    return render_template('ajouter_localisation.html', sites=sites)

@app.route('/equipements')
@login_required
def equipements():
    equipements_list = Equipement.query.all()
    return render_template('equipements.html', equipements=equipements_list)

@app.route('/equipement/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_equipement():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        localisation_id = request.form['localisation_id']
        equipement = Equipement(nom=nom, description=description, localisation_id=localisation_id)
        db.session.add(equipement)
        db.session.commit()
        
        # Gérer les pièces associées
        pieces_ids = request.form.getlist('pieces_ids')
        for piece_id in pieces_ids:
            if piece_id:
                piece_equipement = PieceEquipement(
                    equipement_id=equipement.id,
                    piece_id=int(piece_id)
                )
                db.session.add(piece_equipement)
        
        db.session.commit()
        flash('Équipement ajouté avec succès!', 'success')
        return redirect(url_for('equipements'))
    
    localisations = Localisation.query.all()
    pieces = Piece.query.all()
    return render_template('ajouter_equipement.html', localisations=localisations, pieces=pieces)

@app.route('/pieces')
@login_required
def pieces():
    pieces_list = Piece.query.all()
    lieux_stockage = LieuStockage.query.all()
    return render_template('pieces.html', pieces=pieces_list, lieux_stockage=lieux_stockage)

@app.route('/lieux_stockage')
@login_required
def lieux_stockage():
    lieux_list = LieuStockage.query.all()
    return render_template('lieux_stockage.html', lieux_stockage=lieux_list)

@app.route('/lieu_stockage/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_lieu_stockage():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        lieu = LieuStockage(nom=nom, description=description)
        db.session.add(lieu)
        db.session.commit()
        flash('Lieu de stockage ajouté avec succès!', 'success')
        return redirect(url_for('lieux_stockage'))
    return render_template('ajouter_lieu_stockage.html')

@app.route('/piece/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_piece():
    if request.method == 'POST':
        lieu_stockage_id = request.form.get('lieu_stockage_id')
        if lieu_stockage_id == '':
            lieu_stockage_id = None
        else:
            lieu_stockage_id = int(lieu_stockage_id) if lieu_stockage_id else None
            
        equipement_id = request.form.get('equipement_id')
        if equipement_id == '':
            equipement_id = None
        else:
            equipement_id = int(equipement_id) if equipement_id else None
            
        piece = Piece(
            reference_ste=request.form['reference'],
            reference_magasin=request.form.get('marque', ''),
            item=request.form['designation'],
            description=request.form.get('description', ''),
            lieu_stockage_id=lieu_stockage_id,
            quantite_stock=int(request.form.get('stock_actuel', 0)),
            stock_mini=int(request.form.get('stock_minimum', 0)),
            stock_maxi=int(request.form.get('stock_maxi', 0))
        )
        db.session.add(piece)
        db.session.commit()
        
        # Si un équipement est sélectionné, créer la relation
        if equipement_id:
            piece_equipement = PieceEquipement(
                equipement_id=equipement_id,
                piece_id=piece.id
            )
            db.session.add(piece_equipement)
            db.session.commit()
        
        flash('Pièce ajoutée avec succès!', 'success')
        return redirect(url_for('pieces'))
    
    lieux_stockage = LieuStockage.query.all()
    equipements = Equipement.query.all()
    return render_template('ajouter_piece.html', lieux_stockage=lieux_stockage, equipements=equipements)

@app.route('/maintenances')
@login_required
def maintenances():
    maintenances_list = Maintenance.query.all()
    
    # Séparer les maintenances CO6 et CO7
    maintenances_co6 = []
    maintenances_co7 = []
    
    for maintenance in maintenances_list:
        if maintenance.equipement and maintenance.equipement.localisation:
            localisation_nom = maintenance.equipement.localisation.nom
            if 'CO6' in localisation_nom:
                maintenances_co6.append(maintenance)
            elif 'CO7' in localisation_nom:
                maintenances_co7.append(maintenance)
    
    return render_template('maintenances.html', 
                         maintenances_co6=maintenances_co6, 
                         maintenances_co7=maintenances_co7)

def generate_interventions(maintenance, date_limite=datetime(2030, 12, 31).date()):
    """Génère toutes les interventions futures pour une maintenance jusqu'à la date limite (2030-12-31)."""
    from datetime import timedelta
    
    # Vérifier que la maintenance a une date de première maintenance
    if not maintenance.date_premiere:
        return  # Ne pas générer d'interventions si pas de date de première maintenance
    
    date = maintenance.date_premiere
    interventions = []
    while date <= date_limite:
        interventions.append(Intervention(
            maintenance_id=maintenance.id,
            date_planifiee=date,
            statut='planifiee'
        ))
        if maintenance.periodicite == 'semaine':
            date += timedelta(weeks=1)
        elif maintenance.periodicite == '2_semaines':
            date += timedelta(weeks=2)
        elif maintenance.periodicite == 'mois':
            date += timedelta(days=30)
        elif maintenance.periodicite == '2_mois':
            date += timedelta(days=60)
        elif maintenance.periodicite == '6_mois':
            date += timedelta(days=182)
        elif maintenance.periodicite == '1_an':
            date += timedelta(days=365)
        elif maintenance.periodicite == '2_ans':
            date += timedelta(days=730)
        else:
            break
    db.session.bulk_save_objects(interventions)
    db.session.commit()

@app.route('/maintenance/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_maintenance():
    if request.method == 'POST':
        maintenance = Maintenance(
            equipement_id=request.form['equipement_id'],
            titre=request.form['titre'],
            description='',
            periodicite=request.form['periodicite'],
            date_premiere=datetime.strptime(request.form['date_premiere'], '%Y-%m-%d').date(),
            date_prochaine=datetime.strptime(request.form['date_premiere'], '%Y-%m-%d').date()
        )
        db.session.add(maintenance)
        db.session.commit()

        # Générer toutes les interventions futures (1 an par défaut)
        generate_interventions(maintenance)

        flash('Maintenance ajoutée avec succès!', 'success')
        return redirect(url_for('maintenances'))
    equipements = Equipement.query.all()
    localisations = Localisation.query.all()
    return render_template('ajouter_maintenance.html', equipements=equipements, localisations=localisations)

@app.route('/calendrier')
@login_required
def calendrier():
    date_str = request.args.get('date')
    if date_str:
        date_cible = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date_cible = datetime.now().date()
    # Trouver le lundi de la semaine cible
    lundi = date_cible - timedelta(days=date_cible.weekday())
    dimanche = lundi + timedelta(days=6)
    lundi_courant = datetime.now().date() - timedelta(days=datetime.now().date().weekday())
    interventions = Intervention.query.filter(
        Intervention.date_planifiee >= lundi,
        Intervention.date_planifiee <= dimanche
    ).all()
    # Calculer la prochaine maintenance pour chaque intervention
    for intervention in interventions:
        maintenance = intervention.maintenance
        prochaine_date = None
        if maintenance.periodicite == 'semaine':
            prochaine_date = intervention.date_planifiee + timedelta(weeks=1)
        elif maintenance.periodicite == '2_semaines':
            prochaine_date = intervention.date_planifiee + timedelta(weeks=2)
        elif maintenance.periodicite == 'mois':
            prochaine_date = intervention.date_planifiee + timedelta(days=30)
        elif maintenance.periodicite == '2_mois':
            prochaine_date = intervention.date_planifiee + timedelta(days=60)
        elif maintenance.periodicite == '6_mois':
            prochaine_date = intervention.date_planifiee + timedelta(days=182)
        elif maintenance.periodicite == '1_an':
            prochaine_date = intervention.date_planifiee + timedelta(days=365)
        elif maintenance.periodicite == '2_ans':
            prochaine_date = intervention.date_planifiee + timedelta(days=730)
        intervention.prochaine_maintenance = prochaine_date
    pieces = Piece.query.all()
    return render_template('calendrier.html', interventions=interventions, pieces=pieces, timedelta=timedelta, semaine_lundi=lundi, lundi_courant=lundi_courant)

@app.route('/intervention/realiser/<int:intervention_id>', methods=['POST'])
@login_required
def realiser_intervention(intervention_id):
    intervention = Intervention.query.get_or_404(intervention_id)
    intervention.statut = 'realisee'
    intervention.date_realisee = datetime.now().date()
    intervention.commentaire = request.form.get('commentaire', '')
    
    # Gérer les pièces utilisées
    pieces_utilisees = request.form.getlist('pieces_utilisees')
    quantites = request.form.getlist('quantites')
    
    for i, piece_id in enumerate(pieces_utilisees):
        if piece_id and quantites[i]:
            piece_utilisee = PieceUtilisee(
                intervention_id=intervention.id,
                piece_id=int(piece_id),
                quantite=int(quantites[i])
            )
            db.session.add(piece_utilisee)
            
            # Créer le mouvement de sortie
            piece = Piece.query.get(int(piece_id))
            piece.quantite_stock -= int(quantites[i])
            mouvement = MouvementPiece(
                piece_id=int(piece_id),
                type_mouvement='sortie',
                quantite=int(quantites[i]),
                motif='Maintenance',
                intervention_id=intervention.id
            )
            db.session.add(mouvement)
    
    db.session.commit()
    
    # Générer la prochaine intervention selon la périodicité
    maintenance = intervention.maintenance
    prochaine_date = None
    if maintenance.periodicite == 'semaine':
        prochaine_date = intervention.date_planifiee + timedelta(weeks=1)
    elif maintenance.periodicite == '2_semaines':
        prochaine_date = intervention.date_planifiee + timedelta(weeks=2)
    elif maintenance.periodicite == 'mois':
        prochaine_date = intervention.date_planifiee + timedelta(days=30)
    elif maintenance.periodicite == '2_mois':
        prochaine_date = intervention.date_planifiee + timedelta(days=60)
    elif maintenance.periodicite == '6_mois':
        prochaine_date = intervention.date_planifiee + timedelta(days=182)
    elif maintenance.periodicite == '1_an':
        prochaine_date = intervention.date_planifiee + timedelta(days=365)
    elif maintenance.periodicite == '2_ans':
        prochaine_date = intervention.date_planifiee + timedelta(days=730)

    # Vérifier qu'il n'existe pas déjà une intervention planifiée à cette date
    if prochaine_date:
        existe = Intervention.query.filter_by(maintenance_id=maintenance.id, date_planifiee=prochaine_date).first()
        if not existe:
            nouvelle_intervention = Intervention(
                maintenance_id=maintenance.id,
                date_planifiee=prochaine_date,
                statut='planifiee'
            )
            db.session.add(nouvelle_intervention)
            db.session.commit()

    # Envoyer l'email de confirmation
    envoyer_email_maintenance(intervention)
    
    flash('Intervention réalisée avec succès!', 'success')
    return redirect(url_for('calendrier'))

def envoyer_email_maintenance(intervention):
    try:
        msg = Message(
            f'Maintenance réalisée - {intervention.maintenance.titre}',
            recipients=[current_user.email],
            body=f"""
            Maintenance réalisée avec succès!
            
            Équipement: {intervention.maintenance.equipement.nom}
            Localisation: {intervention.maintenance.equipement.localisation.nom}
            Site: {intervention.maintenance.equipement.localisation.site.nom}
            Date: {intervention.date_realisee}
            Commentaire: {intervention.commentaire}
            """
        )
        mail.send(msg)
    except Exception as e:
        print(f"Erreur lors de l\'envoi de l\'email: {e}")

@app.route('/mouvements')
@login_required
def mouvements():
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    type_mouvement = request.args.get('type_mouvement', 'tous')
    query = MouvementPiece.query
    if type_mouvement == 'entree':
        query = query.filter_by(type_mouvement='entree')
    elif type_mouvement == 'sortie':
        query = query.filter_by(type_mouvement='sortie')
    if date_debut:
        query = query.filter(MouvementPiece.date >= datetime.strptime(date_debut, '%Y-%m-%d'))
    if date_fin:
        query = query.filter(MouvementPiece.date <= datetime.strptime(date_fin, '%Y-%m-%d') + timedelta(days=1))
    mouvements_list = query.order_by(MouvementPiece.date.desc()).all()
    return render_template('mouvements.html', mouvements=mouvements_list, type_mouvement=type_mouvement)

@app.route('/equipement/<int:equipement_id>/pieces', methods=['GET', 'POST'])
@login_required
def gerer_pieces_equipement(equipement_id):
    equipement = Equipement.query.get_or_404(equipement_id)
    
    if request.method == 'POST':
        # Supprimer toutes les associations existantes
        PieceEquipement.query.filter_by(equipement_id=equipement_id).delete()
        
        # Ajouter les nouvelles associations
        pieces_ids = request.form.getlist('pieces_ids')
        for piece_id in pieces_ids:
            if piece_id:
                piece_equipement = PieceEquipement(
                    equipement_id=equipement_id,
                    piece_id=int(piece_id)
                )
                db.session.add(piece_equipement)
        
        db.session.commit()
        flash('Pièces associées mises à jour avec succès!', 'success')
        return redirect(url_for('equipements'))
    
    # Récupérer toutes les pièces et les pièces déjà associées
    toutes_pieces = Piece.query.all()
    pieces_associees = [pe.piece_id for pe in equipement.pieces]
    
    return render_template('gerer_pieces_equipement.html', 
                         equipement=equipement, 
                         toutes_pieces=toutes_pieces,
                         pieces_associees=pieces_associees)

@app.route('/piece/reapprovisionner/<int:piece_id>', methods=['POST'])
@login_required
def reapprovisionner_piece(piece_id):
    piece = Piece.query.get_or_404(piece_id)
    quantite = int(request.form['quantite'])
    piece.quantite_stock += quantite
    
    mouvement = MouvementPiece(
        piece_id=piece_id,
        type_mouvement='entree',
        quantite=quantite,
        motif='Réapprovisionnement'
    )
    db.session.add(mouvement)
    db.session.commit()
    
    flash(f'{quantite} unités ajoutées au stock de {piece.item}', 'success')
    return redirect(url_for('pieces'))

# Routes d'authentification (simplifiées pour la démo)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Veuillez saisir votre identifiant et mot de passe', 'danger')
            return render_template('login.html')
        
        # Rechercher l'utilisateur par son nom d'utilisateur
        user = User.query.filter_by(username=username, active=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Bienvenue {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Identifiant ou mot de passe incorrect', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/site/modifier/<int:site_id>', methods=['GET', 'POST'])
@login_required
def modifier_site(site_id):
    site = Site.query.get_or_404(site_id)
    if request.method == 'POST':
        site.nom = request.form['nom']
        site.description = request.form['description']
        db.session.commit()
        flash('Site modifié avec succès!', 'success')
        return redirect(url_for('sites'))
    return render_template('ajouter_site.html', site=site, edition=True)

@app.route('/localisation/modifier/<int:localisation_id>', methods=['GET', 'POST'])
@login_required
def modifier_localisation(localisation_id):
    localisation = Localisation.query.get_or_404(localisation_id)
    sites = Site.query.all()
    if request.method == 'POST':
        localisation.nom = request.form['nom']
        localisation.description = request.form['description']
        localisation.site_id = request.form['site_id']
        db.session.commit()
        flash('Localisation modifiée avec succès!', 'success')
        return redirect(url_for('localisations'))
    return render_template('ajouter_localisation.html', localisation=localisation, sites=sites, edition=True)

@app.route('/equipement/modifier/<int:equipement_id>', methods=['GET', 'POST'])
@login_required
def modifier_equipement(equipement_id):
    equipement = Equipement.query.get_or_404(equipement_id)
    localisations = Localisation.query.all()
    pieces = Piece.query.all()
    if request.method == 'POST':
        equipement.nom = request.form['nom']
        equipement.description = request.form['description']
        equipement.localisation_id = request.form['localisation_id']
        db.session.commit()
        flash('Équipement modifié avec succès!', 'success')
        return redirect(url_for('equipements'))
    return render_template('ajouter_equipement.html', equipement=equipement, localisations=localisations, pieces=pieces, edition=True)

@app.route('/lieu_stockage/modifier/<int:lieu_stockage_id>', methods=['GET', 'POST'])
@login_required
def modifier_lieu_stockage(lieu_stockage_id):
    lieu = LieuStockage.query.get_or_404(lieu_stockage_id)
    if request.method == 'POST':
        lieu.nom = request.form['nom']
        lieu.description = request.form['description']
        db.session.commit()
        flash('Lieu de stockage modifié avec succès!', 'success')
        return redirect(url_for('lieux_stockage'))
    return render_template('ajouter_lieu_stockage.html', lieu=lieu, edition=True)

@app.route('/maintenance/modifier/<int:maintenance_id>', methods=['GET', 'POST'])
@login_required
def modifier_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    equipements = Equipement.query.all()
    localisations = Localisation.query.all()
    ancienne_periodicite = maintenance.periodicite
    ancienne_date = maintenance.date_premiere
    if request.method == 'POST':
        maintenance.titre = request.form['titre']
        maintenance.description = ''
        maintenance.equipement_id = request.form['equipement_id']
        nouvelle_periodicite = request.form['periodicite']
        nouvelle_date = datetime.strptime(request.form['date_premiere'], '%Y-%m-%d').date()
        changement = (nouvelle_periodicite != ancienne_periodicite) or (nouvelle_date != ancienne_date)
        maintenance.periodicite = nouvelle_periodicite
        maintenance.date_premiere = nouvelle_date
        maintenance.date_prochaine = nouvelle_date
        db.session.commit()
        if changement:
            # Supprimer toutes les interventions planifiées non réalisées futures
            Intervention.query.filter(
                Intervention.maintenance_id == maintenance.id,
                Intervention.statut == 'planifiee',
                Intervention.date_planifiee >= datetime.now().date()
            ).delete(synchronize_session=False)
            db.session.commit()
            # Générer les nouvelles interventions jusqu'en 2030
            generate_interventions(maintenance)
        flash('Maintenance modifiée avec succès!', 'success')
        return redirect(url_for('maintenances'))
    return render_template('ajouter_maintenance.html', maintenance=maintenance, equipements=equipements, localisations=localisations, edition=True)

@app.route('/maintenance/supprimer/<int:maintenance_id>', methods=['POST'])
@login_required
def supprimer_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    db.session.delete(maintenance)
    db.session.commit()
    flash('Maintenance supprimée avec succès.', 'success')
    return redirect(url_for('maintenances'))

@app.route('/maintenance/definir-date/<int:maintenance_id>', methods=['POST'])
@login_required
def definir_date_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    
    try:
        date_premiere = datetime.strptime(request.form['date_premiere'], '%Y-%m-%d').date()
        maintenance.date_premiere = date_premiere
        maintenance.date_prochaine = date_premiere
        maintenance.date_importee = False  # Plus considérée comme importée
        
        # Générer les interventions futures
        generate_interventions(maintenance)
        
        db.session.commit()
        flash('Date de première maintenance définie avec succès !', 'success')
    except Exception as e:
        flash(f'Erreur lors de la définition de la date : {e}', 'danger')
    
    return redirect(url_for('maintenances'))

@app.route('/parametres', methods=['GET', 'POST'])
@login_required
def parametres():
    # Charger la configuration SMTP actuelle
    smtp_config = charger_config_smtp()
    
    if request.method == 'POST':
        # Mise à jour de la configuration SMTP
        smtp_server = request.form.get('smtp_server')
        smtp_port = request.form.get('smtp_port')
        smtp_user = request.form.get('smtp_user')
        smtp_password = request.form.get('smtp_password')
        email_rapport = request.form.get('email_rapport')
        
        # Mettre à jour ou créer les paramètres
        for key, value in [('smtp_server', smtp_server), ('smtp_port', smtp_port), ('smtp_user', smtp_user), ('smtp_password', smtp_password), ('email_rapport', email_rapport)]:
            if value:
                param = Parametre.query.filter_by(cle=key).first()
                if param:
                    param.valeur = value
                else:
                    param = Parametre(cle=key, valeur=value)
                    db.session.add(param)
        
        db.session.commit()
        flash('Configuration mise à jour avec succès!', 'success')
        return redirect(url_for('parametres'))
    
    # Charger tous les paramètres pour le template
    params = {p.cle: p.valeur for p in Parametre.query.all()}
    return render_template('parametres.html', 
                         smtp_server=params.get('smtp_server', 'smtp.gmail.com'),
                         smtp_port=params.get('smtp_port', '587'),
                         smtp_user=params.get('smtp_user', ''),
                         smtp_password=params.get('smtp_password', ''),
                         email_rapport=params.get('email_rapport', ''))

@app.route('/parametres/utilisateurs')
@login_required
def gestion_utilisateurs():
    """Page de gestion des utilisateurs et permissions"""
    users = User.query.filter_by(active=True).all()
    pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
             'maintenances', 'calendrier', 'mouvements', 'parametres']
    
    # Récupérer les permissions pour chaque utilisateur
    users_permissions = {}
    for user in users:
        permissions = get_user_permissions(user.id)
        users_permissions[user.id] = permissions
    
    return render_template('gestion_utilisateurs.html', 
                         users=users, 
                         pages=pages, 
                         users_permissions=users_permissions)

@app.route('/parametres/utilisateur/creer', methods=['POST'])
@login_required
def creer_utilisateur():
    """Créer un nouvel utilisateur"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Tous les champs sont obligatoires', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Vérifier si l'utilisateur existe déjà
    if User.query.filter_by(username=username).first():
        flash('Ce nom d\'utilisateur existe déjà', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Créer l'utilisateur
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Créer les permissions par défaut (aucune)
    create_user_permissions(user.id)
    
    flash(f'Utilisateur {username} créé avec succès', 'success')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/parametres/utilisateur/<int:user_id>/permissions', methods=['POST'])
@login_required
def modifier_permissions(user_id):
    """Modifier les permissions d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
             'maintenances', 'calendrier', 'mouvements', 'parametres']
    
    permissions_data = {}
    for page in pages:
        permissions_data[page] = {
            'access': request.form.get(f'{page}_access') == 'on'
        }
    
    update_user_permissions(user_id, permissions_data)
    flash(f'Permissions de {user.username} mises à jour', 'success')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/parametres/utilisateur/permissions-bulk', methods=['POST'])
@login_required
def modifier_permissions_bulk():
    """Modifier les permissions de tous les utilisateurs en lot"""
    pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
             'maintenances', 'calendrier', 'mouvements', 'parametres']
    
    # Récupérer toutes les permissions du formulaire
    permissions_form = request.form.getlist('permissions')
    
    # Traiter chaque utilisateur
    for user_id_str in request.form:
        if user_id_str.startswith('permissions[') and user_id_str.endswith(']'):
            # Extraire l'ID utilisateur et la page
            # Format: permissions[user_id][page]
            parts = user_id_str.replace('permissions[', '').replace(']', '').split('[')
            if len(parts) == 2:
                user_id = int(parts[0])
                page = parts[1]
                
                # Vérifier si cette permission est cochée
                is_checked = request.form.get(user_id_str) == '1'
                
                # Mettre à jour la permission
                permission = UserPermission.query.filter_by(user_id=user_id, page=page).first()
                if permission:
                    permission.can_access = is_checked
                else:
                    # Créer une nouvelle permission si elle n'existe pas
                    permission = UserPermission(user_id=user_id, page=page, can_access=is_checked)
                    db.session.add(permission)
    
    db.session.commit()
    flash('Toutes les permissions ont été mises à jour', 'success')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/parametres/utilisateur/<int:user_id>/supprimer', methods=['POST'])
@login_required
def supprimer_utilisateur(user_id):
    """Supprimer un utilisateur (désactiver)"""
    user = User.query.get_or_404(user_id)
    
    # Empêcher la suppression de son propre compte
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    user.active = False
    db.session.commit()
    
    flash(f'Utilisateur {user.username} supprimé', 'success')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/parametres/utilisateur/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_password_utilisateur(user_id):
    """Réinitialiser le mot de passe d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    if not new_password:
        flash('Le nouveau mot de passe est obligatoire', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    user.set_password(new_password)
    db.session.commit()
    
    flash(f'Mot de passe de {user.username} réinitialisé', 'success')
    return redirect(url_for('gestion_utilisateurs'))

def charger_config_smtp():
    params = {p.cle: p.valeur for p in Parametre.query.all()}
    smtp_server = params.get('smtp_server', app.config.get('MAIL_SERVER'))
    smtp_port = int(params.get('smtp_port', app.config.get('MAIL_PORT', 587)))
    smtp_user = params.get('smtp_user', app.config.get('MAIL_USERNAME'))
    smtp_password = params.get('smtp_password', app.config.get('MAIL_PASSWORD'))
    
    # Mise à jour de la configuration globale
    app.config.update(
        MAIL_SERVER=smtp_server,
        MAIL_PORT=smtp_port,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=smtp_user,
        MAIL_PASSWORD=smtp_password,
        MAIL_DEFAULT_SENDER=smtp_user
    )
    
    # Reconfigurer l'instance mail globale
    global mail
    mail.init_app(app)
    
    return smtp_user

@app.route('/parametres/test_email', methods=['POST'])
@login_required
def test_email():
    from flask_mail import Mail, Message
    # Charger la configuration sauvegardée
    charger_config_smtp()
    
    # Récupérer l'email de destination depuis le formulaire
    email_rapport = request.form.get('email_rapport')
    
    try:
        msg = Message('Test de configuration email', 
                     recipients=[email_rapport], 
                     body='Ceci est un test de la configuration SMTP de l\'application de maintenance.', 
                     sender=app.config.get('MAIL_USERNAME'))
        mail.send(msg)
        flash('Email de test envoyé avec succès !', 'success')
    except Exception as e:
        flash(f'Erreur lors de l\'envoi : {e}', 'danger')
    return redirect(url_for('parametres'))

@app.route('/calendrier/envoyer_rapport', methods=['POST'])
@login_required
def envoyer_rapport():
    try:
        # Récupérer la semaine actuellement affichée dans le calendrier
        date_str = request.args.get('date')
        if date_str:
            date_cible = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date_cible = datetime.now().date()
        
        # Calculer le lundi et dimanche de la semaine cible (même logique que le calendrier)
        lundi = date_cible - timedelta(days=date_cible.weekday())
        dimanche = lundi + timedelta(days=6)
        
        # Récupérer les interventions de la semaine
        interventions = Intervention.query.filter(
            Intervention.date_planifiee >= lundi,
            Intervention.date_planifiee <= dimanche
        ).all()
        
        print(f"🔍 Debug: {len(interventions)} interventions trouvées pour la semaine {lundi.isocalendar()[1]}")
        for interv in interventions:
            print(f"  - Intervention {interv.id}: {interv.maintenance.titre} le {interv.date_planifiee}")
        
        # Récupérer les mouvements de la semaine
        mouvements = MouvementPiece.query.filter(
            MouvementPiece.date >= datetime.combine(lundi, datetime.min.time()),
            MouvementPiece.date <= datetime.combine(dimanche, datetime.max.time())
        ).all()
        
        print(f"🔍 Debug: {len(mouvements)} mouvements trouvés pour la semaine {lundi.isocalendar()[1]}")
        
        # Récupérer l'email de destination
        email_param = Parametre.query.filter_by(cle='email_rapport').first()
        email_dest = email_param.valeur if email_param else None
        if not email_dest:
            flash("Aucune adresse email de rapport n'est configurée.", 'danger')
            return redirect(url_for('calendrier'))
        
        # Charger la config SMTP dynamique
        charger_config_smtp()
        
        # Générer le PDF avec FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Logo si présent
        try:
            pdf.image('static/logo.png', x=10, y=8, w=25)
        except:
            pass
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Rapport de maintenance - Semaine {lundi.isocalendar()[1]}', ln=1, align='C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Période du {lundi.strftime("%d/%m/%Y")} au {dimanche.strftime("%d/%m/%Y")}', ln=1, align='C')
        pdf.ln(5)
        
        # Section maintenances
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Maintenances de la semaine', ln=1)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(50, 8, 'Titre', 1)
        pdf.cell(35, 8, 'Équipement', 1)
        pdf.cell(25, 8, 'Statut', 1)
        pdf.cell(50, 8, 'Commentaire', 1)
        pdf.cell(0, 8, 'Pièces utilisées', 1, ln=1)
        pdf.set_font('Arial', '', 10)
        
        # Si pas d'interventions, essayer de générer les interventions manquantes
        if not interventions:
            print("🔍 Aucune intervention trouvée, génération des interventions manquantes...")
            maintenances_actives = Maintenance.query.filter_by(active=True).all()
            print(f"🔍 {len(maintenances_actives)} maintenances actives trouvées")
            
            # Générer les interventions pour chaque maintenance active
            for maintenance in maintenances_actives:
                try:
                    # Vérifier si des interventions existent déjà pour cette maintenance
                    existing_interventions = Intervention.query.filter_by(maintenance_id=maintenance.id).count()
                    if existing_interventions == 0:
                        print(f"🔧 Génération des interventions pour maintenance {maintenance.id}: {maintenance.titre}")
                        generate_interventions(maintenance)
                except Exception as e:
                    print(f"Erreur lors de la génération des interventions pour maintenance {maintenance.id}: {e}")
            
            # Récupérer à nouveau les interventions après génération
            interventions = Intervention.query.filter(
                Intervention.date_planifiee >= lundi,
                Intervention.date_planifiee <= dimanche
            ).all()
            print(f"🔍 Après génération: {len(interventions)} interventions trouvées")
            
            # Si toujours pas d'interventions, afficher les maintenances actives
            if not interventions:
                print("🔍 Aucune intervention générée, affichage des maintenances actives...")
            
            for maintenance in maintenances_actives:
                try:
                    titre = maintenance.titre or ''
                    equip = maintenance.equipement.nom if maintenance.equipement else 'N/A'
                    statut = 'Active'
                    commentaire = maintenance.description or '-'
                    pieces = 'N/A'
                    
                    # Calculer la hauteur max de la ligne
                    y_before = pdf.get_y()
                    x = pdf.get_x()
                    w_titre, w_equip, w_statut, w_com, w_pieces = 50, 35, 25, 50, 40
                    h = 8
                    
                    # multi_cell pour chaque champ, on retient la hauteur max
                    pdf.multi_cell(w_titre, h, titre, border=1, align='L', max_line_height=pdf.font_size)
                    y_after = pdf.get_y()
                    max_h = y_after - y_before
                    
                    pdf.set_xy(x + w_titre, y_before)
                    pdf.multi_cell(w_equip, h, equip, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    pdf.set_xy(x + w_titre + w_equip, y_before)
                    pdf.multi_cell(w_statut, h, statut, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    pdf.set_xy(x + w_titre + w_equip + w_statut, y_before)
                    pdf.multi_cell(w_com, h, commentaire, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    pdf.set_xy(x + w_titre + w_equip + w_statut + w_com, y_before)
                    pdf.multi_cell(w_pieces, h, pieces, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    # Passer à la ligne suivante
                    pdf.set_y(y_before + max_h)
                except Exception as e:
                    print(f"Erreur lors du traitement de la maintenance {maintenance.id}: {e}")
                    continue
        else:
            print(f"🔍 {len(interventions)} interventions trouvées, génération du rapport...")
        
        for intervention in interventions:
            try:
                # Préparer les contenus avec gestion d'erreurs
                titre = intervention.maintenance.titre or ''
                equip = intervention.maintenance.equipement.nom if intervention.maintenance.equipement else 'N/A'
                statut = 'Réalisée' if intervention.statut == 'realisee' else 'Non réalisée'
                commentaire = intervention.commentaire or '-'
                
                # Gestion des pièces utilisées
                pieces_list = []
                for pu in intervention.pieces_utilisees:
                    try:
                        piece = pu.piece if hasattr(pu, 'piece') and pu.piece else Piece.query.get(pu.piece_id)
                        if piece:
                            piece_name = piece.item or piece.description or f"Pièce {piece.id}"
                            pieces_list.append(f"{piece_name} ({pu.quantite})")
                    except:
                        pieces_list.append(f"Pièce {pu.piece_id} ({pu.quantite})")
                
                pieces = ', '.join(pieces_list) if pieces_list else 'Aucune'
                
                # Calculer la hauteur max de la ligne
                y_before = pdf.get_y()
                x = pdf.get_x()
                w_titre, w_equip, w_statut, w_com, w_pieces = 50, 35, 25, 50, 40
                h = 8
                
                # multi_cell pour chaque champ, on retient la hauteur max
                pdf.multi_cell(w_titre, h, titre, border=1, align='L', max_line_height=pdf.font_size)
                y_after = pdf.get_y()
                max_h = y_after - y_before
                
                pdf.set_xy(x + w_titre, y_before)
                pdf.multi_cell(w_equip, h, equip, border=1, align='L', max_line_height=pdf.font_size)
                max_h = max(max_h, pdf.get_y() - y_before)
                
                pdf.set_xy(x + w_titre + w_equip, y_before)
                pdf.multi_cell(w_statut, h, statut, border=1, align='L', max_line_height=pdf.font_size)
                max_h = max(max_h, pdf.get_y() - y_before)
                
                pdf.set_xy(x + w_titre + w_equip + w_statut, y_before)
                pdf.multi_cell(w_com, h, commentaire, border=1, align='L', max_line_height=pdf.font_size)
                max_h = max(max_h, pdf.get_y() - y_before)
                
                pdf.set_xy(x + w_titre + w_equip + w_statut + w_com, y_before)
                pdf.multi_cell(w_pieces, h, pieces, border=1, align='L', max_line_height=pdf.font_size)
                max_h = max(max_h, pdf.get_y() - y_before)
                
                # Passer à la ligne suivante
                pdf.set_y(y_before + max_h)
            except Exception as e:
                print(f"Erreur lors du traitement de l'intervention {intervention.id}: {e}")
                continue
        
        # Nouvelle page pour les mouvements de stock
        if mouvements:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Mouvements de stock de la semaine', ln=1)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(30, 8, 'Date', 1)
            pdf.cell(40, 8, 'Pièce', 1)
            pdf.cell(20, 8, 'Type', 1)
            pdf.cell(20, 8, 'Quantité', 1)
            pdf.cell(40, 8, 'Motif', 1)
            pdf.cell(0, 8, 'Intervention', 1, ln=1)
            pdf.set_font('Arial', '', 10)
            
            for mouvement in mouvements:
                try:
                    y_before = pdf.get_y()
                    x = pdf.get_x()
                    w_date, w_piece, w_type, w_qte, w_motif, w_interv = 30, 40, 20, 20, 40, 40
                    h = 8
                    date = mouvement.date.strftime('%d/%m/%Y')
                    piece = mouvement.piece.item[:40] if mouvement.piece and mouvement.piece.item else 'N/A'
                    type_mv = mouvement.type_mouvement.title()
                    qte = str(mouvement.quantite)
                    motif = (mouvement.motif or '-')[:40]
                    
                    # Gestion de l'intervention
                    interv = None
                    if hasattr(mouvement, 'intervention') and mouvement.intervention:
                        interv = mouvement.intervention
                    elif mouvement.intervention_id:
                        interv = Intervention.query.get(mouvement.intervention_id)
                    
                    txt = f"{interv.maintenance.titre[:15]}" if interv and interv.maintenance else '-'
                    
                    # multi_cell pour chaque champ, on retient la hauteur max
                    pdf.multi_cell(w_date, h, date, border=1, align='L', max_line_height=pdf.font_size)
                    y_after = pdf.get_y()
                    max_h = y_after - y_before
                    
                    pdf.set_xy(x + w_date, y_before)
                    pdf.multi_cell(w_piece, h, piece, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    pdf.set_xy(x + w_date + w_piece, y_before)
                    pdf.multi_cell(w_type, h, type_mv, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    pdf.set_xy(x + w_date + w_piece + w_type, y_before)
                    pdf.multi_cell(w_qte, h, qte, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    pdf.set_xy(x + w_date + w_piece + w_type + w_qte, y_before)
                    pdf.multi_cell(w_motif, h, motif, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    pdf.set_xy(x + w_date + w_piece + w_type + w_qte + w_motif, y_before)
                    pdf.multi_cell(w_interv, h, txt, border=1, align='L', max_line_height=pdf.font_size)
                    max_h = max(max_h, pdf.get_y() - y_before)
                    
                    pdf.set_y(y_before + max_h)
                except Exception as e:
                    print(f"Erreur lors du traitement du mouvement {mouvement.id}: {e}")
                    continue
        
        # Sauvegarder le PDF en mémoire
        pdf_data = pdf.output(dest='S')
        if isinstance(pdf_data, str):
            pdf_data = pdf_data.encode('latin1')
        
        # Envoyer le mail avec le PDF en pièce jointe
        msg = Message(
            subject=f"Rapport de maintenance semaine {lundi.isocalendar()[1]}",
            recipients=[email_dest],
            body=f"Veuillez trouver ci-joint le rapport de maintenance de la semaine {lundi.strftime('%d/%m/%Y')} au {dimanche.strftime('%d/%m/%Y')}.",
            sender=app.config.get('MAIL_USERNAME')
        )
        msg.attach(f"rapport_maintenance_semaine_{lundi.isocalendar()[1]}.pdf", "application/pdf", pdf_data)
        
        try:
            mail.send(msg)
            flash('Rapport envoyé avec succès !', 'success')
        except Exception as e:
            flash(f'Erreur lors de l\'envoi du rapport : {str(e)}', 'danger')
        
        return redirect(url_for('calendrier'))
        
    except Exception as e:
        print(f"Erreur lors de la génération du rapport: {e}")
        flash(f'Erreur lors de la génération du rapport : {str(e)}', 'danger')
        return redirect(url_for('calendrier'))

@app.route('/piece/supprimer/<int:piece_id>', methods=['POST'])
@login_required
def supprimer_piece(piece_id):
    try:
        piece = Piece.query.get_or_404(piece_id)
        
        # Supprimer d'abord les relations pour éviter les erreurs de clés étrangères
        
        # 1. Supprimer les mouvements de pièces
        MouvementPiece.query.filter_by(piece_id=piece_id).delete()
        
        # 2. Supprimer les pièces utilisées dans les interventions
        PieceUtilisee.query.filter_by(piece_id=piece_id).delete()
        
        # 3. Supprimer les associations pièce-équipement
        PieceEquipement.query.filter_by(piece_id=piece_id).delete()
        
        # 4. Maintenant on peut supprimer la pièce
        db.session.delete(piece)
        db.session.commit()
        
        flash('Pièce supprimée avec succès.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression : {str(e)}', 'danger')
        print(f"Erreur suppression pièce {piece_id}: {e}")
    
    return redirect(url_for('pieces'))

@app.route('/lieu_stockage/supprimer/<int:lieu_stockage_id>', methods=['POST'])
@login_required
def supprimer_lieu_stockage(lieu_stockage_id):
    lieu = LieuStockage.query.get_or_404(lieu_stockage_id)
    db.session.delete(lieu)
    db.session.commit()
    flash('Lieu de stockage supprimé avec succès.', 'success')
    return redirect(url_for('lieux_stockage'))

@app.route('/equipement/supprimer/<int:equipement_id>', methods=['POST'])
@login_required
def supprimer_equipement(equipement_id):
    equipement = Equipement.query.get_or_404(equipement_id)
    db.session.delete(equipement)
    db.session.commit()
    flash('Équipement supprimé avec succès.', 'success')
    return redirect(url_for('equipements'))

@app.route('/localisation/supprimer/<int:localisation_id>', methods=['POST'])
@login_required
def supprimer_localisation(localisation_id):
    localisation = Localisation.query.get_or_404(localisation_id)
    db.session.delete(localisation)
    db.session.commit()
    flash('Localisation supprimée avec succès.', 'success')
    return redirect(url_for('localisations'))

@app.route('/site/supprimer/<int:site_id>', methods=['POST'])
@login_required
def supprimer_site(site_id):
    site = Site.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    flash('Site supprimé avec succès.', 'success')
    return redirect(url_for('sites'))

@app.route('/vider-sites', methods=['POST'])
@login_required
def vider_sites():
    """Vide uniquement les sites et leurs données associées"""
    try:
        # Supprimer les données dans l'ordre pour respecter les contraintes de clés étrangères
        
        # 1. Mouvements de pièces (liés aux interventions)
        MouvementPiece.query.delete()
        
        # 2. Pièces utilisées (liées aux interventions)
        PieceUtilisee.query.delete()
        
        # 3. Interventions (liées aux maintenances)
        Intervention.query.delete()
        
        # 4. Maintenances (liées aux équipements)
        Maintenance.query.delete()
        
        # 5. Associations pièces-équipements
        PieceEquipement.query.delete()
        
        # 6. Équipements (liés aux localisations)
        Equipement.query.delete()
        
        # 7. Localisations (liées aux sites)
        Localisation.query.delete()
        
        # 8. Sites
        Site.query.delete()
        
        # Valider les changements
        db.session.commit()
        
        flash('Tous les sites et leurs données associées ont été supprimés avec succès !', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression : {str(e)}', 'danger')
    
    return redirect(url_for('sites'))

@app.route('/vider-localisations', methods=['POST'])
@login_required
def vider_localisations():
    """Vide uniquement les localisations et leurs données associées"""
    try:
        # Supprimer les données dans l'ordre pour respecter les contraintes de clés étrangères
        
        # 1. Mouvements de pièces (liés aux interventions)
        MouvementPiece.query.delete()
        
        # 2. Pièces utilisées (liées aux interventions)
        PieceUtilisee.query.delete()
        
        # 3. Interventions (liées aux maintenances)
        Intervention.query.delete()
        
        # 4. Maintenances (liées aux équipements)
        Maintenance.query.delete()
        
        # 5. Associations pièces-équipements
        PieceEquipement.query.delete()
        
        # 6. Équipements (liés aux localisations)
        Equipement.query.delete()
        
        # 7. Localisations
        Localisation.query.delete()
        
        # Valider les changements
        db.session.commit()
        
        flash('Toutes les localisations et leurs données associées ont été supprimées avec succès !', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression : {str(e)}', 'danger')
    
    return redirect(url_for('localisations'))

@app.route('/vider-equipements', methods=['POST'])
@login_required
def vider_equipements():
    """Vide uniquement les équipements et leurs données associées"""
    try:
        # Supprimer les données dans l'ordre pour respecter les contraintes de clés étrangères
        
        # 1. Mouvements de pièces (liés aux interventions)
        MouvementPiece.query.delete()
        
        # 2. Pièces utilisées (liées aux interventions)
        PieceUtilisee.query.delete()
        
        # 3. Interventions (liées aux maintenances)
        Intervention.query.delete()
        
        # 4. Maintenances (liées aux équipements)
        Maintenance.query.delete()
        
        # 5. Associations pièces-équipements
        PieceEquipement.query.delete()
        
        # 6. Équipements
        Equipement.query.delete()
        
        # Valider les changements
        db.session.commit()
        
        flash('Tous les équipements et leurs données associées ont été supprimés avec succès !', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression : {str(e)}', 'danger')
    
    return redirect(url_for('equipements'))

@app.route('/vider-pieces', methods=['POST'])
@login_required
def vider_pieces():
    """Vide uniquement les pièces et leurs données associées"""
    try:
        # Supprimer les données dans l'ordre pour respecter les contraintes de clés étrangères
        
        # 1. Mouvements de pièces
        MouvementPiece.query.delete()
        
        # 2. Pièces utilisées (liées aux interventions)
        PieceUtilisee.query.delete()
        
        # 3. Associations pièces-équipements
        PieceEquipement.query.delete()
        
        # 4. Pièces
        Piece.query.delete()
        
        # Valider les changements
        db.session.commit()
        
        flash('Toutes les pièces et leurs données associées ont été supprimées avec succès !', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression : {str(e)}', 'danger')
    
    return redirect(url_for('pieces'))

# --- Import/Export Excel/CSV ---
ENTITES_MODELES = {
    'site': ['id', 'nom', 'description'],
    'localisation': ['id', 'nom', 'description', 'site_id'],
    'equipement': ['id', 'nom', 'description', 'localisation_id'],
    'lieu_stockage': ['id', 'nom', 'description'],
    'piece': ['id', 'reference_ste', 'reference_magasin', 'item', 'description', 'lieu_stockage_id', 'quantite_stock', 'stock_mini', 'stock_maxi'],
    'maintenance': ['id', 'titre', 'equipement_id', 'localisation_id', 'periodicite']
}
ENTITES_MODELS = {
    'site': Site,
    'localisation': Localisation,
    'equipement': Equipement,
    'lieu_stockage': LieuStockage,
    'piece': Piece,
    'maintenance': Maintenance
}

# Colonnes d'aide pour les foreign keys
ENTITES_AIDES = {
    'localisation': {'site_id': ('site_nom', 'site', 'nom')},
    'equipement': {'localisation_id': ('localisation_nom', 'localisation', 'nom')},
    'piece': {'lieu_stockage_id': ('lieu_stockage_nom', 'lieu_stockage', 'nom')},
    'maintenance': {
        'equipement_id': ('equipement_nom', 'equipement', 'nom'),
        'localisation_id': ('localisation_nom', 'localisation', 'nom')
    }
}

@app.route('/parametres/modele/<entite>.<format>')
@login_required
def download_modele(entite, format):
    if entite not in ENTITES_MODELES:
        return 'Entité inconnue', 400
    colonnes = ENTITES_MODELES[entite][:]
    # Ajout des colonnes d'aide
    if entite in ENTITES_AIDES:
        for fk, (col_aide, _, _) in ENTITES_AIDES[entite].items():
            colonnes.append(col_aide)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format}') as tmp:
        if format == 'xlsx':
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = 'Données'
            
            # Écrire les en-têtes
            for col, header in enumerate(colonnes, 1):
                ws.cell(row=1, column=col, value=header)
            
            # Ajouter quelques exemples de données selon l'entité
            if entite == 'site':
                exemples = [
                    {'id': '', 'nom': 'Site A', 'description': 'Description du site A'},
                    {'id': '', 'nom': 'Site B', 'description': 'Description du site B'}
                ]
            elif entite == 'localisation':
                exemples = [
                    {'id': '', 'nom': 'Localisation 1', 'description': 'Description', 'site_id': '1', 'site_nom': 'Site A'},
                    {'id': '', 'nom': 'Localisation 2', 'description': 'Description', 'site_id': '1', 'site_nom': 'Site A'}
                ]
            elif entite == 'equipement':
                exemples = [
                    {'id': '', 'nom': 'Équipement 1', 'description': 'Description', 'localisation_id': '1', 'localisation_nom': 'Localisation 1'},
                    {'id': '', 'nom': 'Équipement 2', 'description': 'Description', 'localisation_id': '1', 'localisation_nom': 'Localisation 1'}
                ]
            elif entite == 'piece':
                exemples = [
                    {'id': '', 'reference_ste': 'REF001', 'reference_magasin': 'Marque A', 'item': 'Pièce 1', 'description': 'Description', 'lieu_stockage_id': '1', 'lieu_stockage_nom': 'Entrepôt', 'quantite_stock': '10', 'stock_mini': '5', 'stock_maxi': '20'},
                    {'id': '', 'reference_ste': 'REF002', 'reference_magasin': 'Marque B', 'item': 'Pièce 2', 'description': 'Description', 'lieu_stockage_id': '1', 'lieu_stockage_nom': 'Entrepôt', 'quantite_stock': '15', 'stock_mini': '3', 'stock_maxi': '25'}
                ]
            elif entite == 'maintenance':
                exemples = [
                    {'id': '', 'titre': 'Maintenance préventive', 'equipement_id': '1', 'equipement_nom': 'Équipement 1', 'localisation_id': '1', 'localisation_nom': 'Localisation 1', 'periodicite': 'mois'},
                    {'id': '', 'titre': 'Maintenance corrective', 'equipement_id': '2', 'equipement_nom': 'Équipement 2', 'localisation_id': '1', 'localisation_nom': 'Localisation 1', 'periodicite': 'semaine'}
                ]
            elif entite == 'lieu_stockage':
                exemples = [
                    {'id': '', 'nom': 'Entrepôt principal', 'description': 'Entrepôt principal du site'},
                    {'id': '', 'nom': 'Entrepôt secondaire', 'description': 'Entrepôt secondaire'}
                ]
            else:
                exemples = []
            
            # Écrire les exemples
            for row_idx, exemple in enumerate(exemples, 2):
                for col_idx, header in enumerate(colonnes, 1):
                    ws.cell(row=row_idx, column=col_idx, value=exemple.get(header, ''))
            
            wb.save(tmp.name)
            
        elif format == 'csv':
            with open(tmp.name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=colonnes)
                writer.writeheader()
                # Ajouter les mêmes exemples pour CSV
                if entite == 'site':
                    writer.writerow({'id': '', 'nom': 'Site A', 'description': 'Description du site A'})
                    writer.writerow({'id': '', 'nom': 'Site B', 'description': 'Description du site B'})
                elif entite == 'localisation':
                    writer.writerow({'id': '', 'nom': 'Localisation 1', 'description': 'Description', 'site_id': '1', 'site_nom': 'Site A'})
                    writer.writerow({'id': '', 'nom': 'Localisation 2', 'description': 'Description', 'site_id': '1', 'site_nom': 'Site A'})
                elif entite == 'equipement':
                    writer.writerow({'id': '', 'nom': 'Équipement 1', 'description': 'Description', 'localisation_id': '1', 'localisation_nom': 'Localisation 1'})
                    writer.writerow({'id': '', 'nom': 'Équipement 2', 'description': 'Description', 'localisation_id': '1', 'localisation_nom': 'Localisation 1'})
                elif entite == 'piece':
                    writer.writerow({'id': '', 'reference_ste': 'REF001', 'reference_magasin': 'Marque A', 'item': 'Pièce 1', 'description': 'Description', 'lieu_stockage_id': '1', 'lieu_stockage_nom': 'Entrepôt', 'quantite_stock': '10', 'stock_mini': '5', 'stock_maxi': '20'})
                    writer.writerow({'id': '', 'reference_ste': 'REF002', 'reference_magasin': 'Marque B', 'item': 'Pièce 2', 'description': 'Description', 'lieu_stockage_id': '1', 'lieu_stockage_nom': 'Entrepôt', 'quantite_stock': '15', 'stock_mini': '3', 'stock_maxi': '25'})
                elif entite == 'maintenance':
                    writer.writerow({'id': '', 'titre': 'Maintenance préventive', 'equipement_id': '1', 'equipement_nom': 'Équipement 1', 'localisation_id': '1', 'localisation_nom': 'Localisation 1', 'periodicite': 'mois'})
                    writer.writerow({'id': '', 'titre': 'Maintenance corrective', 'equipement_id': '2', 'equipement_nom': 'Équipement 2', 'localisation_id': '1', 'localisation_nom': 'Localisation 1', 'periodicite': 'semaine'})
                elif entite == 'lieu_stockage':
                    writer.writerow({'id': '', 'nom': 'Entrepôt principal', 'description': 'Entrepôt principal du site'})
                    writer.writerow({'id': '', 'nom': 'Entrepôt secondaire', 'description': 'Entrepôt secondaire'})
        else:
            return 'Format non supporté', 400
        tmp.flush()
        return send_file(tmp.name, as_attachment=True, download_name=f'modele_{entite}.{format}')

@app.route('/parametres/modele-maintenances.xlsx')
@login_required
def download_modele_maintenances():
    """Génère un modèle Excel spécial pour l'import des maintenances avec onglets de référence"""
    
    # Onglet principal Maintenances
    data_maintenances = []
    
    # Onglet Équipements
    equipements = Equipement.query.all()
    data_equipements = [
        {'Nom': e.nom, 'Localisation': e.localisation.nom, 'Description': e.description or ''}
        for e in equipements
    ]
    
    # Onglet Localisations
    localisations = Localisation.query.all()
    data_localisations = [
        {'Nom': l.nom, 'Site': l.site.nom, 'Description': l.description or ''}
        for l in localisations
    ]
    
    # Onglet Périodicités
    data_periodicites = [
        {'Périodicité': 'semaine', 'Description': 'Toutes les semaines'},
        {'Périodicité': '2_semaines', 'Description': 'Toutes les 2 semaines'},
        {'Périodicité': 'mois', 'Description': 'Tous les mois'},
        {'Périodicité': '2_mois', 'Description': 'Tous les 2 mois'},
        {'Périodicité': '6_mois', 'Description': 'Tous les 6 mois'},
        {'Périodicité': '1_an', 'Description': 'Tous les ans'},
        {'Périodicité': '2_ans', 'Description': 'Tous les 2 ans'}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        from openpyxl import Workbook
        wb = Workbook()
        
        # Supprimer la feuille par défaut
        wb.remove(wb.active)
        
        # Créer les onglets
        ws_maintenances = wb.create_sheet('Maintenances')
        ws_equipements = wb.create_sheet('Équipements')
        ws_localisations = wb.create_sheet('Localisations')
        ws_periodicites = wb.create_sheet('Périodicités')
        
        # Écrire les données
        # Maintenances
        headers_maintenances = ['id', 'titre', 'equipement_nom', 'localisation_nom', 'periodicite']
        for col, header in enumerate(headers_maintenances, 1):
            ws_maintenances.cell(row=1, column=col, value=header)
        
        # Équipements
        if data_equipements:
            headers_equipements = list(data_equipements[0].keys())
            for col, header in enumerate(headers_equipements, 1):
                ws_equipements.cell(row=1, column=col, value=header)
            for row_idx, row_data in enumerate(data_equipements, 2):
                for col_idx, header in enumerate(headers_equipements, 1):
                    ws_equipements.cell(row=row_idx, column=col_idx, value=row_data.get(header))
        
        # Localisations
        if data_localisations:
            headers_localisations = list(data_localisations[0].keys())
            for col, header in enumerate(headers_localisations, 1):
                ws_localisations.cell(row=1, column=col, value=header)
            for row_idx, row_data in enumerate(data_localisations, 2):
                for col_idx, header in enumerate(headers_localisations, 1):
                    ws_localisations.cell(row=row_idx, column=col_idx, value=row_data.get(header))
        
        # Périodicités
        headers_periodicites = ['Périodicité', 'Description']
        for col, header in enumerate(headers_periodicites, 1):
            ws_periodicites.cell(row=1, column=col, value=header)
        for row_idx, row_data in enumerate(data_periodicites, 2):
            for col_idx, header in enumerate(headers_periodicites, 1):
                ws_periodicites.cell(row=row_idx, column=col_idx, value=row_data.get(header))
        
        wb.save(tmp.name)
        tmp.flush()
        return send_file(tmp.name, as_attachment=True, download_name='modele_maintenances.xlsx')

@app.route('/parametres/export/<entite>.xlsx')
@login_required
def export_donnees(entite):
    if entite not in ENTITES_MODELS:
        return 'Entité inconnue', 400
    Model = ENTITES_MODELS[entite]
    colonnes = [c.key for c in inspect(Model).columns]
    donnees = Model.query.all()
    data = [ {col: getattr(obj, col) for col in colonnes} for obj in donnees ]
    # Ajout des colonnes d'aide
    if entite in ENTITES_AIDES:
        for fk, (col_aide, table, champ) in ENTITES_AIDES[entite].items():
            for i, obj in enumerate(donnees):
                fk_id = getattr(obj, fk)
                aide_val = ''
                if fk_id:
                    fk_model = ENTITES_MODELS[table]
                    fk_obj = fk_model.query.get(fk_id)
                    if fk_obj:
                        aide_val = getattr(fk_obj, champ)
                data[i][col_aide] = aide_val
        colonnes += [str(v[0]) for v in ENTITES_AIDES[entite].values()]
    # Génération du deuxième onglet de correspondance
    correspondances = {}
    if entite == 'localisation':
        correspondances['Sites'] = [{'ID': s.id, 'Nom': s.nom} for s in Site.query.all()]
    elif entite == 'equipement':
        correspondances['Localisations'] = [{'ID': l.id, 'Nom': l.nom} for l in Localisation.query.all()]
    elif entite == 'piece':
        correspondances['Lieux de stockage'] = [{'ID': l.id, 'Nom': l.nom} for l in LieuStockage.query.all()]
    elif entite == 'maintenance':
        correspondances['Équipements'] = [{'ID': e.id, 'Nom': e.nom} for e in Equipement.query.all()]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        from openpyxl import Workbook
        wb = Workbook()
        
        # Supprimer la feuille par défaut
        wb.remove(wb.active)
        
        # Créer l'onglet Données
        ws_donnees = wb.create_sheet('Données')
        
        # Écrire les en-têtes
        for col, header in enumerate(colonnes, 1):
            ws_donnees.cell(row=1, column=col, value=header)
        
        # Écrire les données
        for row_idx, row_data in enumerate(data, 2):
            for col_idx, header in enumerate(colonnes, 1):
                ws_donnees.cell(row=row_idx, column=col_idx, value=row_data.get(header))
        
        # Créer les onglets de correspondance
        for nom, data_corresp in correspondances.items():
            ws_corresp = wb.create_sheet(nom)
            if data_corresp:
                headers_corresp = list(data_corresp[0].keys())
                for col, header in enumerate(headers_corresp, 1):
                    ws_corresp.cell(row=1, column=col, value=header)
                for row_idx, row_data in enumerate(data_corresp, 2):
                    for col_idx, header in enumerate(headers_corresp, 1):
                        ws_corresp.cell(row=row_idx, column=col_idx, value=row_data.get(header))
        
        wb.save(tmp.name)
        tmp.flush()
        return send_file(tmp.name, as_attachment=True, download_name=f'{entite}_export.xlsx')

@app.route('/parametres/import/<entite>', methods=['POST'])
@login_required
def import_donnees(entite):
    if entite not in ENTITES_MODELS:
        flash('Entité inconnue', 'danger')
        return redirect(url_for('parametres'))
    Model = ENTITES_MODELS[entite]
    file = request.files.get('fichier')
    if not file or not file.filename:
        flash('Aucun fichier envoyé', 'danger')
        return redirect(url_for('parametres'))
    try:
        filename = file.filename.lower()
        if filename.endswith('.xlsx'):
            # Sauvegarder le fichier temporairement
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                file.save(tmp.name)
                result = read_excel_simple(tmp.name)
                data = result['data']
                colonnes = result['columns']
        elif filename.endswith('.csv'):
            file.seek(0)
            content = file.read().decode('utf-8')
            result = read_csv_simple(content)
            data = result['data']
            colonnes = result['columns']
        else:
            flash('Format de fichier non supporté', 'danger')
            return redirect(url_for('parametres'))
        
        model_columns = [c.key for c in inspect(Model).columns]
        erreurs = []
        lignes_a_importer = []
        # Gestion des colonnes d'aide pour foreign keys
        aides = ENTITES_AIDES.get(entite, {})
        
        for idx, row in enumerate(data):
            obj = None
            row_id = row.get('id', None)
            if row_id is not None and not (isinstance(row_id, float) and is_na(row_id)):
                obj = Model.query.get(int(row_id))
            data = {}
            fk_error = False
            champs_manquants = []
            for col in model_columns:
                if col == 'id':
                    continue
                val = row.get(col, None)
                if val is None or (isinstance(val, float) and is_na(val)) or val == '':
                    # Pour les pièces de rechange, on tolère les champs manquants sauf item et reference_ste
                    if entite == 'piece' and col not in ['item', 'reference_ste']:
                        champs_manquants.append(col)
                        continue
                    # Si c'est une foreign key, tenter de récupérer via la colonne d'aide
                    if col in aides:
                        col_aide, table, champ = aides[col]
                        val_aide = row.get(col_aide, None)
                        if val_aide and not (isinstance(val_aide, float) and is_na(val_aide)):
                            fk_model = ENTITES_MODELS[table]
                            fk_obj = fk_model.query.filter(getattr(fk_model, champ)==val_aide).first()
                            if fk_obj:
                                val = fk_obj.id
                            else:
                                erreurs.append(f"Ligne {int(idx)+2} : {col_aide} '{val_aide}' introuvable dans la base")
                                fk_error = True
                                break
                        else:
                            erreurs.append(f"Ligne {int(idx)+2} : {col_aide} non renseigné (obligatoire)")
                            fk_error = True
                            break
                    elif entite == 'piece' and col in ['item', 'reference_ste']:
                        # Pour les pièces, on permet les champs manquants mais on les signale
                        champs_manquants.append(col)
                        val = None  # Permettre les valeurs NULL
                        data[col] = val
                        continue
                    else:
                        continue
                # Conversion des types spéciaux
                if col in ['active']:
                    val = bool(val) if str(val).lower() not in ['0', 'false', 'non', ''] else False
                if col.startswith('date_'):
                    try:
                        val = parse_date(str(val)).date()
                    except Exception:
                        erreurs.append(f"Ligne {int(idx)+2}: Date invalide pour '{col}' : {val}")
                        fk_error = True
                        break
                if col.endswith('_id'):
                    fk_model = None
                    if col == 'site_id': fk_model = ENTITES_MODELS['site']
                    if col == 'localisation_id': fk_model = ENTITES_MODELS['localisation']
                    if col == 'equipement_id': fk_model = ENTITES_MODELS['equipement']
                    if col == 'lieu_stockage_id': fk_model = ENTITES_MODELS['lieu_stockage']
                    
                    # Gestion spéciale pour les maintenances
                    if entite == 'maintenance' and col == 'equipement_id':
                        # Pour les maintenances, on peut avoir equipement_nom au lieu de equipement_id
                        equipement_nom = row.get('equipement_nom')
                        if equipement_nom and not (isinstance(equipement_nom, float) and is_na(equipement_nom)):
                            equipement = Equipement.query.filter_by(nom=equipement_nom).first()
                            if equipement:
                                val = equipement.id
                            else:
                                erreurs.append(f"Ligne {int(idx)+2}: Équipement '{equipement_nom}' introuvable")
                                fk_error = True
                                break
                        else:
                            erreurs.append(f"Ligne {int(idx)+2}: equipement_nom non renseigné")
                            fk_error = True
                            break
                    else:
                        try:
                            if fk_model and not fk_model.query.get(int(val)):
                                erreurs.append(f"Ligne {int(idx)+2}: {col} {val} n'existe pas")
                                fk_error = True
                                break
                            if isinstance(val, (str, float, int)) and not isinstance(val, bool):
                                val = int(val)
                        except Exception:
                            erreurs.append(f"Ligne {int(idx)+2}: {col} valeur non convertible : {val}")
                            fk_error = True
                            break
                if col in ['quantite_stock', 'stock_mini', 'stock_maxi']:
                    try:
                        if val is None or (isinstance(val, float) and is_na(val)):
                            # Valeurs par défaut pour les pièces
                            if col == 'quantite_stock':
                                val = 0
                            elif col == 'stock_mini':
                                val = 0
                            elif col == 'stock_maxi':
                                val = 10
                        elif isinstance(val, (str, float, int)) and not isinstance(val, bool):
                            val = int(val)
                    except Exception:
                        erreurs.append(f"Ligne {int(idx)+2}: Valeur entière attendue pour '{col}' : {val}")
                        fk_error = True
                        break
                data[col] = val
            if fk_error:
                continue
            if entite == 'piece' and champs_manquants:
                erreurs.append(f"Ligne {int(idx)+2} : champs non obligatoires manquants pour la pièce de rechange : {', '.join(champs_manquants)} (enregistré quand même)")
            lignes_a_importer.append((obj, data))
        # Détecter les doublons pour les pièces
        doublons = []
        references_traitees = set()  # Pour éviter les doublons dans le même fichier
        
        if entite == 'piece':
            for obj, data in lignes_a_importer:
                if not obj:  # Nouvelle pièce
                    reference_ste = data.get('reference_ste')
                    item = data.get('item')
                    
                    # Vérifier d'abord les doublons dans le fichier
                    if reference_ste and reference_ste in references_traitees:
                        doublons.append({
                            'nouvelle': data,
                            'existante': None,
                            'type': 'doublon_fichier'
                        })
                        continue
                    
                    if reference_ste:
                        references_traitees.add(reference_ste)
                        # Chercher les doublons par référence STE en base
                        piece_existante = Piece.query.filter_by(reference_ste=reference_ste).first()
                        if piece_existante:
                            doublons.append({
                                'nouvelle': data,
                                'existante': piece_existante,
                                'type': 'reference_ste'
                            })
                    elif item:
                        # Chercher les doublons par item
                        piece_existante = Piece.query.filter_by(item=item).first()
                        if piece_existante:
                            doublons.append({
                                'nouvelle': data,
                                'existante': piece_existante,
                                'type': 'item'
                            })
        
        # Si des doublons sont détectés, les stocker en session pour affichage
        if doublons:
            # Créer une liste des références des doublons pour les exclure de l'import
            doublons_references = set()
            for d in doublons:
                if d['type'] == 'reference_ste' and d['nouvelle'].get('reference_ste'):
                    doublons_references.add(d['nouvelle']['reference_ste'])
                elif d['type'] == 'item' and d['nouvelle'].get('item'):
                    doublons_references.add(d['nouvelle']['item'])
            
            # Filtrer les lignes à importer pour exclure les doublons
            lignes_a_importer_filtrees = []
            for obj, data in lignes_a_importer:
                if not obj:  # Nouvelle pièce
                    reference_ste = data.get('reference_ste')
                    item = data.get('item')
                    # Vérifier si cette ligne est un doublon
                    is_doublon = False
                    if reference_ste and reference_ste in doublons_references:
                        is_doublon = True
                    elif item and item in doublons_references:
                        is_doublon = True
                    
                    if not is_doublon:
                        lignes_a_importer_filtrees.append((obj, data))
                else:
                    # Pièce existante à mettre à jour
                    lignes_a_importer_filtrees.append((obj, data))
            
            # Remplacer la liste originale
            lignes_a_importer = lignes_a_importer_filtrees
            
            # IMPORTANT : Importer les pièces non-doublons MAINTENANT
            for obj, data in lignes_a_importer:
                if obj:
                    for k, v in data.items():
                        setattr(obj, k, v)
                else:
                    obj = Model(**data)
                    db.session.add(obj)
            db.session.commit()
            
            # Stocker les doublons en session
            session['doublons_pieces'] = [
                {
                    'nouvelle': {
                        'reference_ste': d['nouvelle'].get('reference_ste'),
                        'reference_magasin': d['nouvelle'].get('reference_magasin'),
                        'item': d['nouvelle'].get('item'),
                        'description': d['nouvelle'].get('description'),
                        'quantite_stock': d['nouvelle'].get('quantite_stock', 0),
                        'stock_mini': d['nouvelle'].get('stock_mini', 0),
                        'stock_maxi': d['nouvelle'].get('stock_maxi', 10)
                    },
                    'existante': {
                        'id': d['existante'].id,
                        'reference_ste': d['existante'].reference_ste,
                        'reference_magasin': d['existante'].reference_magasin,
                        'item': d['existante'].item,
                        'description': d['existante'].description,
                        'quantite_stock': d['existante'].quantite_stock,
                        'stock_mini': d['existante'].stock_mini,
                        'stock_maxi': d['existante'].stock_maxi
                    },
                    'type': d['type']
                } for d in doublons
            ]
            flash(f'Importation réussie ! {len(lignes_a_importer)} pièces importées. {len(doublons)} doublon(s) détecté(s) - veuillez les examiner.', 'success')
            return redirect(url_for('gerer_doublons_pieces'))
        
        # Pour les pièces, on importe même avec des erreurs non bloquantes
        if erreurs and entite != 'piece':
            flash('Erreurs lors de l\'import :<br>' + '<br>'.join(erreurs), 'danger')
            return redirect(url_for('parametres'))
        elif erreurs and entite == 'piece':
            # Pour les pièces, on affiche les avertissements mais on continue
            flash('Importation avec avertissements :<br>' + '<br>'.join(erreurs), 'warning')
        for obj, data in lignes_a_importer:
            if obj:
                for k, v in data.items():
                    setattr(obj, k, v)
            else:
                obj = Model(**data)
                db.session.add(obj)
        db.session.commit()
        flash(f'Importation réussie pour {entite}', 'success')
    except Exception as e:
        flash(f'Erreur lors de l\'import : {e}', 'danger')
    return redirect(url_for('parametres'))

@app.route('/parametres/import-maintenances', methods=['POST'])
@login_required
def import_maintenances():
    """Import spécial pour les maintenances sans date de début"""
    print("🔍 Début import_maintenances()")
    print(f"🔍 Méthode: {request.method}")
    print(f"🔍 Fichiers reçus: {list(request.files.keys())}")
    print(f"🔍 URL: {request.url}")
    print(f"🔍 User: {current_user.username if current_user.is_authenticated else 'Non connecté'}")
    
    file = request.files.get('fichier')
    if not file or not file.filename:
        print("❌ Aucun fichier envoyé")
        flash('Aucun fichier envoyé', 'danger')
        return redirect(url_for('parametres'))
    
    print(f"📁 Fichier reçu: {file.filename}")
    print(f"📁 Taille fichier: {len(file.read())} bytes")
    file.seek(0)  # Remettre le curseur au début
    
    try:
        filename = file.filename.lower()
        if filename.endswith('.xlsx'):
            # Lire le fichier Excel avec openpyxl
            from openpyxl import load_workbook
            wb = load_workbook(file, data_only=True)
            
            # Lire l'onglet Maintenances
            if 'Maintenances' not in wb.sheetnames:
                flash('Onglet "Maintenances" introuvable dans le fichier Excel', 'danger')
                return redirect(url_for('parametres'))
            
            ws_maintenances = wb['Maintenances']
            maintenances_data = []
            
            # Lire les données (en-têtes + données)
            for row in ws_maintenances.iter_rows(min_row=2, values_only=True):
                if any(cell for cell in row):  # Ignorer les lignes vides
                    maintenances_data.append(row)
            
            # Convertir en format plus facile à traiter
            df_maintenances = []
            for row in maintenances_data:
                if len(row) >= 4:  # Au moins titre, equipement_nom, localisation_nom, periodicite
                    df_maintenances.append({
                        'titre': row[1] if len(row) > 1 else '',
                        'equipement_nom': row[2] if len(row) > 2 else '',
                        'localisation_nom': row[3] if len(row) > 3 else '',
                        'periodicite': row[4] if len(row) > 4 else ''
                    })
            
        else:
            flash('Format de fichier non supporté. Utilisez un fichier Excel (.xlsx)', 'danger')
            return redirect(url_for('parametres'))
        
        erreurs = []
        maintenances_importees = 0
        
        for idx, row in enumerate(df_maintenances):
            try:
                titre = row.get('titre')
                equipement_nom = row.get('equipement_nom')
                localisation_nom = row.get('localisation_nom')
                periodicite = row.get('periodicite')
                
                if not titre or not equipement_nom or not localisation_nom or not periodicite:
                    erreurs.append(f"Ligne {int(idx)+2}: Champs obligatoires manquants")
                    continue
                
                # Trouver l'équipement
                equipement = Equipement.query.filter_by(nom=equipement_nom).first()
                if not equipement:
                    erreurs.append(f"Ligne {int(idx)+2}: Équipement '{equipement_nom}' introuvable")
                    continue
                
                # Vérifier que l'équipement est dans la bonne localisation
                if equipement.localisation.nom != localisation_nom:
                    erreurs.append(f"Ligne {int(idx)+2}: L\'équipement '{equipement_nom}' n\'est pas dans la localisation '{localisation_nom}'")
                    continue
                
                # Vérifier la périodicité
                periodicites_valides = ['semaine', '2_semaines', 'mois', '2_mois', '6_mois', '1_an', '2_ans']
                if periodicite not in periodicites_valides:
                    erreurs.append(f"Ligne {int(idx)+2}: Périodicité '{periodicite}' invalide. Valeurs autorisées: {', '.join(periodicites_valides)}")
                    continue
                
                # Créer la maintenance sans date
                maintenance = Maintenance(
                    equipement_id=equipement.id,
                    titre=titre,
                    periodicite=periodicite,
                    date_premiere=None,
                    date_prochaine=None,
                    date_importee=True  # Marquer comme importée sans date
                )
                
                db.session.add(maintenance)
                maintenances_importees += 1
                
            except Exception as e:
                erreurs.append(f"Ligne {int(idx)+2}: Erreur - {str(e)}")
                continue
        
        if erreurs:
            db.session.rollback()
            flash('Erreurs lors de l\'import :<br>' + '<br>'.join(erreurs), 'danger')
            return redirect(url_for('parametres'))
        
        db.session.commit()
        print(f"✅ Import réussi: {maintenances_importees} maintenances importées")
        flash(f'Importation réussie ! {maintenances_importees} maintenances importées sans date de début.', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur lors de l'import: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Erreur lors de l\'import : {e}', 'danger')
    
    print("🏁 Fin import_maintenances()")
    return redirect(url_for('parametres'))

# Test route pour vérifier que la fonction est accessible
@app.route('/test-import-maintenances')
@login_required
def test_import_maintenances():
    return "Route import_maintenances accessible !"

@app.route('/parametres/gerer-doublons-pieces', methods=['GET', 'POST'])
@login_required
def gerer_doublons_pieces():
    if 'doublons_pieces' not in session:
        flash('Aucun doublon à gérer', 'info')
        return redirect(url_for('parametres'))
    
    doublons = session['doublons_pieces']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'fusionner_tout':
            # Fusionner tous les doublons
            for doublon in doublons:
                piece_existante = None
                if doublon['existante'] and 'id' in doublon['existante']:
                    piece_existante = Piece.query.get(doublon['existante']['id'])
                if piece_existante:
                    # Mettre à jour avec les nouvelles données
                    nouvelle = doublon['nouvelle']
                    if nouvelle.get('reference_ste'):
                        piece_existante.reference_ste = nouvelle['reference_ste']
                    if nouvelle.get('reference_magasin'):
                        piece_existante.reference_magasin = nouvelle['reference_magasin']
                    if nouvelle.get('item'):
                        piece_existante.item = nouvelle['item']
                    if nouvelle.get('description'):
                        piece_existante.description = nouvelle['description']
                    if nouvelle.get('quantite_stock') is not None:
                        piece_existante.quantite_stock = nouvelle['quantite_stock']
                    if nouvelle.get('stock_mini') is not None:
                        piece_existante.stock_mini = nouvelle['stock_mini']
                    if nouvelle.get('stock_maxi') is not None:
                        piece_existante.stock_maxi = nouvelle['stock_maxi']
            
            db.session.commit()
            del session['doublons_pieces']
            flash('Tous les doublons ont été fusionnés avec succès', 'success')
            return redirect(url_for('parametres'))
        
        elif action == 'ignorer_tout':
            # Ignorer tous les doublons
            del session['doublons_pieces']
            flash('Tous les doublons ont été ignorés', 'info')
            return redirect(url_for('parametres'))
        
        elif action == 'fusionner_selection':
            # Fusionner seulement les doublons sélectionnés
            doublons_a_fusionner = request.form.getlist('fusionner')
            for doublon_id in doublons_a_fusionner:
                doublon = doublons[int(doublon_id)]
                piece_existante = None
                if doublon['existante'] and 'id' in doublon['existante']:
                    piece_existante = Piece.query.get(doublon['existante']['id'])
                if piece_existante:
                    nouvelle = doublon['nouvelle']
                    if nouvelle.get('reference_ste'):
                        piece_existante.reference_ste = nouvelle['reference_ste']
                    if nouvelle.get('reference_magasin'):
                        piece_existante.reference_magasin = nouvelle['reference_magasin']
                    if nouvelle.get('item'):
                        piece_existante.item = nouvelle['item']
                    if nouvelle.get('description'):
                        piece_existante.description = nouvelle['description']
                    if nouvelle.get('quantite_stock') is not None:
                        piece_existante.quantite_stock = nouvelle['quantite_stock']
                    if nouvelle.get('stock_mini') is not None:
                        piece_existante.stock_mini = nouvelle['stock_mini']
                    if nouvelle.get('stock_maxi') is not None:
                        piece_existante.stock_maxi = nouvelle['stock_maxi']
            db.session.commit()
            del session['doublons_pieces']
            flash('Doublons sélectionnés fusionnés avec succès', 'success')
            return redirect(url_for('parametres'))
    
    return render_template('gerer_doublons_pieces.html', doublons=doublons)

@app.route('/parametres/taille-tables')
@login_required
def taille_tables():
    chemin_db = os.path.join(app.root_path, 'instance', 'maintenance.db')
    conn = sqlite3.connect(chemin_db)
    cur = conn.cursor()
    # Taille totale du fichier .db
    taille_fichier = os.path.getsize(chemin_db)
    # Liste des tables utilisateur
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cur.fetchall()]
    lignes = {}
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        nb = cur.fetchone()[0]
        lignes[table] = nb
    conn.close()
    return jsonify({
        'taille_fichier': taille_fichier,
        'lignes': lignes
    })

@app.route('/piece/modifier/<int:piece_id>', methods=['POST', 'GET'])
@login_required
def modifier_piece(piece_id):
    piece = Piece.query.get_or_404(piece_id)
    if request.method == 'POST':
        piece.reference_ste = request.form['reference_ste']
        piece.reference_magasin = request.form['reference_magasin']
        piece.item = request.form['item']
        piece.description = request.form['description']
        lieu_stockage_id = request.form.get('lieu_stockage_id')
        if lieu_stockage_id == '':
            lieu_stockage_id = None
        else:
            lieu_stockage_id = int(lieu_stockage_id) if lieu_stockage_id else None
        piece.quantite_stock = int(request.form['quantite_stock'])
        piece.stock_mini = int(request.form['stock_mini'])
        piece.stock_maxi = int(request.form['stock_maxi'])
        db.session.commit()
        flash('Pièce modifiée avec succès!', 'success')
        return redirect(url_for('pieces'))
    # GET: afficher le formulaire pré-rempli (optionnel)
    lieux_stockage = LieuStockage.query.all()
    equipements = Equipement.query.all()
    return render_template('ajouter_piece.html', piece=piece, lieux_stockage=lieux_stockage, equipements=equipements, edition=True)

# Initialisation automatique au démarrage de l'application
with app.app_context():
    try:
        print("🔍 Initialisation de la base de données...")
        db.create_all()
        print("✅ Tables créées avec succès!")
        
        # Créer un utilisateur admin par défaut si aucun n'existe
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("🔍 Création de l'utilisateur admin...")
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            
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
            print("✅ Utilisateur admin créé avec succès!")
            print("📋 Identifiants: admin / admin123")
        else:
            print("✅ Utilisateur admin existe déjà")
            
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    app.run(debug=True) 