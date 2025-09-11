#!/usr/bin/env python3
"""
Script de test pour vérifier l'envoi de mails pour les commandes
"""

import os
import sys
from flask import Flask
from flask_mail import Mail, Message

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configuration email
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

def test_envoi_mail():
    """Test d'envoi de mail simple"""
    try:
        print("🔍 Configuration SMTP:")
        print(f"   Serveur: {app.config['MAIL_SERVER']}")
        print(f"   Port: {app.config['MAIL_PORT']}")
        print(f"   Utilisateur: {app.config['MAIL_USERNAME']}")
        print(f"   Mot de passe: {'***' if app.config['MAIL_PASSWORD'] else 'NON CONFIGURÉ'}")
        print(f"   Expéditeur par défaut: {app.config['MAIL_DEFAULT_SENDER']}")
        
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            print("❌ Configuration SMTP incomplète!")
            return False
        
        # Créer un message de test
        msg = Message(
            subject="Test envoi mail commande",
            body="Ceci est un test d'envoi de mail pour les commandes.",
            recipients=[app.config['MAIL_USERNAME']]  # Envoyer à soi-même pour le test
        )
        
        print("📧 Tentative d'envoi du mail de test...")
        mail.send(msg)
        print("✅ Mail envoyé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du mail: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de configuration SMTP pour les commandes")
    print("=" * 50)
    
    with app.app_context():
        success = test_envoi_mail()
        
    if success:
        print("\n✅ Configuration SMTP OK - Les mails devraient fonctionner")
    else:
        print("\n❌ Problème de configuration SMTP - Vérifiez vos paramètres")
