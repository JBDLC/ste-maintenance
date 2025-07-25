#!/usr/bin/env python3
"""
Migration pour ajouter la table ErreurImportMaintenance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import ErreurImportMaintenance

def migrate():
    """Créer la table ErreurImportMaintenance"""
    with app.app_context():
        print("🔧 Création de la table ErreurImportMaintenance...")
        
        # Créer la table
        db.create_all()
        
        print("✅ Migration terminée !")

if __name__ == '__main__':
    migrate() 