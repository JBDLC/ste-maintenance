#!/usr/bin/env python3
"""
Tests basiques pour l'application de maintenance
"""

import unittest
import os
import tempfile
from app import app, db, Site, Localisation, Equipement, Piece, LieuStockage

class MaintenanceTestCase(unittest.TestCase):
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Utiliser une base de données temporaire pour les tests
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_home_page(self):
        """Test de la page d'accueil"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_login_page(self):
        """Test de la page de connexion"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_create_site(self):
        """Test de création d'un site"""
        with app.app_context():
            site = Site(nom='Test Site', description='Site de test')
            db.session.add(site)
            db.session.commit()
            
            # Vérifier que le site a été créé
            site_from_db = Site.query.filter_by(nom='Test Site').first()
            self.assertIsNotNone(site_from_db)
            self.assertEqual(site_from_db.description, 'Site de test')
    
    def test_create_localisation(self):
        """Test de création d'une localisation"""
        with app.app_context():
            # Créer d'abord un site
            site = Site(nom='Test Site', description='Site de test')
            db.session.add(site)
            db.session.commit()
            
            # Créer une localisation
            localisation = Localisation(
                nom='Test Localisation',
                description='Localisation de test',
                site_id=site.id
            )
            db.session.add(localisation)
            db.session.commit()
            
            # Vérifier que la localisation a été créée
            loc_from_db = Localisation.query.filter_by(nom='Test Localisation').first()
            self.assertIsNotNone(loc_from_db)
            self.assertEqual(loc_from_db.site_id, site.id)
    
    def test_create_equipement(self):
        """Test de création d'un équipement"""
        with app.app_context():
            # Créer un site
            site = Site(nom='Test Site', description='Site de test')
            db.session.add(site)
            db.session.commit()
            
            # Créer une localisation
            localisation = Localisation(
                nom='Test Localisation',
                description='Localisation de test',
                site_id=site.id
            )
            db.session.add(localisation)
            db.session.commit()
            
            # Créer un équipement
            equipement = Equipement(
                nom='Test Equipment',
                description='Équipement de test',
                localisation_id=localisation.id
            )
            db.session.add(equipement)
            db.session.commit()
            
            # Vérifier que l'équipement a été créé
            equip_from_db = Equipement.query.filter_by(nom='Test Equipment').first()
            self.assertIsNotNone(equip_from_db)
            self.assertEqual(equip_from_db.localisation_id, localisation.id)
    
    def test_create_piece(self):
        """Test de création d'une pièce"""
        with app.app_context():
            # Créer un lieu de stockage
            lieu = LieuStockage(nom='Test Stockage', description='Lieu de test')
            db.session.add(lieu)
            db.session.commit()
            
            # Créer une pièce
            piece = Piece(
                reference_ste='STE-001',
                reference_magasin='MAG-001',
                item='Test Piece',
                description='Pièce de test',
                lieu_stockage_id=lieu.id,
                quantite_stock=10,
                stock_mini=2,
                stock_maxi=20
            )
            db.session.add(piece)
            db.session.commit()
            
            # Vérifier que la pièce a été créée
            piece_from_db = Piece.query.filter_by(reference_ste='STE-001').first()
            self.assertIsNotNone(piece_from_db)
            self.assertEqual(piece_from_db.quantite_stock, 10)
    
    def test_database_connection(self):
        """Test de connexion à la base de données"""
        with app.app_context():
            # Essayer de créer et récupérer un objet simple
            site = Site(nom='Connection Test', description='Test de connexion')
            db.session.add(site)
            db.session.commit()
            
            # Vérifier que l'objet peut être récupéré
            site_from_db = Site.query.filter_by(nom='Connection Test').first()
            self.assertIsNotNone(site_from_db)

if __name__ == '__main__':
    print("🧪 Lancement des tests...")
    unittest.main(verbosity=2) 