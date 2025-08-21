#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier la logique de classification des interventions
dans le calendrier de maintenance.
"""

from datetime import datetime, timedelta
from app import app, db
from models import Intervention, Maintenance, Equipement, Localisation, Site

def test_classification_calendrier():
    """Test de la logique de classification des interventions"""
    
    with app.app_context():
        # Récupérer la date actuelle
        date_cible = datetime.now().date()
        
        # Trouver le lundi de la semaine cible
        lundi = date_cible - timedelta(days=date_cible.weekday())
        dimanche = lundi + timedelta(days=6)
        
        print(f"Test de classification pour la semaine du {lundi} au {dimanche}")
        print("=" * 60)
        
        # Récupérer toutes les interventions de la semaine
        interventions_list = Intervention.query.filter(
            Intervention.date_planifiee >= lundi,
            Intervention.date_planifiee <= dimanche
        ).all()
        
        print(f"Nombre total d'interventions trouvées : {len(interventions_list)}")
        
        # Séparer les interventions CO6 et CO7 par sous-parties
        interventions_co6_ste = []
        interventions_co6_cab = []
        interventions_co6_step = []
        interventions_co7_ste = []
        interventions_co7_cab = []
        interventions_co7_step = []
        
        for intervention in interventions_list:
            if intervention.maintenance.equipement and intervention.maintenance.equipement.localisation:
                localisation_nom = intervention.maintenance.equipement.localisation.nom
                equipement_nom = intervention.maintenance.equipement.nom
                
                print(f"\nIntervention: {intervention.maintenance.titre}")
                print(f"  Équipement: {equipement_nom}")
                print(f"  Localisation: {localisation_nom}")
                
                # Déterminer la sous-partie basée sur le nom de l'équipement ET la localisation
                equipement_nom_upper = equipement_nom.upper()
                localisation_nom_upper = localisation_nom.upper()
                sous_partie = 'STE'  # Par défaut
                
                # Priorité : STEP > CAB > STE
                # Vérifier d'abord dans le nom de l'équipement, puis dans la localisation
                if 'STEP' in equipement_nom_upper or 'STEP' in localisation_nom_upper:
                    sous_partie = 'STEP'
                elif 'CAB' in equipement_nom_upper or 'CAB' in localisation_nom_upper:
                    sous_partie = 'CAB'
                # Si ni STEP ni CAB, alors c'est STE
                
                print(f"  Sous-partie détectée: {sous_partie}")
                
                # Classer selon CO6/CO7 et sous-partie
                if 'CO6' in localisation_nom:
                    if sous_partie == 'STE':
                        interventions_co6_ste.append(intervention)
                        print(f"  → Classé dans CO6 STE")
                    elif sous_partie == 'CAB':
                        interventions_co6_cab.append(intervention)
                        print(f"  → Classé dans CO6 CAB")
                    elif sous_partie == 'STEP':
                        interventions_co6_step.append(intervention)
                        print(f"  → Classé dans CO6 STEP")
                elif 'CO7' in localisation_nom:
                    if sous_partie == 'STE':
                        interventions_co7_ste.append(intervention)
                        print(f"  → Classé dans CO7 STE")
                    elif sous_partie == 'CAB':
                        interventions_co7_cab.append(intervention)
                        print(f"  → Classé dans CO7 CAB")
                    elif sous_partie == 'STEP':
                        interventions_co7_step.append(intervention)
                        print(f"  → Classé dans CO7 STEP")
                else:
                    print(f"  → Non classé (pas CO6 ni CO7)")
        
        print("\n" + "=" * 60)
        print("RÉSUMÉ DE LA CLASSIFICATION:")
        print(f"CO6 STE: {len(interventions_co6_ste)} interventions")
        print(f"CO6 CAB: {len(interventions_co6_cab)} interventions")
        print(f"CO6 STEP: {len(interventions_co6_step)} interventions")
        print(f"CO7 STE: {len(interventions_co7_ste)} interventions")
        print(f"CO7 CAB: {len(interventions_co7_cab)} interventions")
        print(f"CO7 STEP: {len(interventions_co7_step)} interventions")
        
        # Afficher quelques détails pour chaque catégorie
        if interventions_co6_ste:
            print(f"\nCO6 STE - Exemples:")
            for i, intervention in enumerate(interventions_co6_ste[:3]):
                print(f"  {i+1}. {intervention.maintenance.titre} - {intervention.maintenance.equipement.nom}")
        
        if interventions_co6_cab:
            print(f"\nCO6 CAB - Exemples:")
            for i, intervention in enumerate(interventions_co6_cab[:3]):
                print(f"  {i+1}. {intervention.maintenance.titre} - {intervention.maintenance.equipement.nom}")
        
        if interventions_co6_step:
            print(f"\nCO6 STEP - Exemples:")
            for i, intervention in enumerate(interventions_co6_step[:3]):
                print(f"  {i+1}. {intervention.maintenance.titre} - {intervention.maintenance.equipement.nom}")
        
        if interventions_co7_ste:
            print(f"\nCO7 STE - Exemples:")
            for i, intervention in enumerate(interventions_co7_ste[:3]):
                print(f"  {i+1}. {intervention.maintenance.titre} - {intervention.maintenance.equipement.nom}")
        
        if interventions_co7_cab:
            print(f"\nCO7 CAB - Exemples:")
            for i, intervention in enumerate(interventions_co7_cab[:3]):
                print(f"  {i+1}. {intervention.maintenance.titre} - {intervention.maintenance.equipement.nom}")
        
        if interventions_co7_step:
            print(f"\nCO7 STEP - Exemples:")
            for i, intervention in enumerate(interventions_co7_step[:3]):
                print(f"  {i+1}. {intervention.maintenance.titre} - {intervention.maintenance.equipement.nom}")

if __name__ == "__main__":
    test_classification_calendrier() 