#!/usr/bin/env python3
"""
Script de diagnostic pour Render
"""

import sys
import os

def check_app_import():
    """Vérifier l'import de l'application"""
    try:
        print("🔍 Tentative d'import de app...")
        import app
        print("✅ App importé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'import de app: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_pdf_generation():
    """Vérifier la génération PDF"""
    try:
        print("🔍 Test de génération PDF...")
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Test PDF', ln=1)
        
        pdf_data = pdf.output(dest='S')
        print(f"✅ PDF généré avec succès ({len(pdf_data)} bytes)")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la génération PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """Vérifier la base de données"""
    try:
        print("🔍 Test de connexion base de données...")
        import app
        from app import db
        
        with app.app_context():
            # Test simple de connexion
            result = db.engine.execute("SELECT 1")
            print("✅ Connexion base de données OK")
            return True
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Diagnostic Render - Démarrage")
    
    # Tests
    app_ok = check_app_import()
    pdf_ok = check_pdf_generation()
    db_ok = check_database()
    
    print("\n📊 Résumé:")
    print(f"  - App import: {'✅' if app_ok else '❌'}")
    print(f"  - PDF génération: {'✅' if pdf_ok else '❌'}")
    print(f"  - Base de données: {'✅' if db_ok else '❌'}")
    
    if app_ok and pdf_ok and db_ok:
        print("\n🎉 Tous les tests passent !")
        sys.exit(0)
    else:
        print("\n💥 Certains tests échouent")
        sys.exit(1) 