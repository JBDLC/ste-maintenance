#!/usr/bin/env python3
"""
Script de test pour vérifier la sauvegarde des paramètres
"""

import requests
import json

# URL de base (ajustez selon votre configuration)
BASE_URL = "http://localhost:5000"

def test_parametres():
    """Test de la sauvegarde des paramètres"""
    
    # Données de test
    test_data = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': '587',
        'smtp_user': 'test@example.com',
        'smtp_password': 'testpassword',
        'email_rapport': 'rapport@example.com'
    }
    
    print("🧪 Test de sauvegarde des paramètres...")
    
    try:
        # Envoyer les données de test
        response = requests.post(f"{BASE_URL}/parametres", data=test_data)
        
        if response.status_code == 200:
            print("✅ Sauvegarde réussie!")
            
            # Vérifier que les données sont bien sauvegardées
            response_get = requests.get(f"{BASE_URL}/parametres")
            if response_get.status_code == 200:
                print("✅ Page de paramètres accessible")
            else:
                print("❌ Erreur lors de l'accès à la page de paramètres")
                
        else:
            print(f"❌ Erreur lors de la sauvegarde: {response.status_code}")
            print(f"Contenu: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'application")
        print("Assurez-vous que l'application est lancée sur http://localhost:5000")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_parametres() 