#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, timedelta

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Maintenance, Intervention

def test_database():
    with app.app_context():
        print("🔍 Test de la base de données...")
        
        # Récupérer toutes les maintenances
        maintenances = Maintenance.query.all()
        print(f"📊 Nombre total de maintenances: {len(maintenances)}")
        
        for m in maintenances:
            equip = m.equipement.nom if m.equipement else 'N/A'
            print(f"  - Maintenance {m.id}: {m.titre} (Équipement: {equip}, Active: {m.active})")
        
        # Test pour la semaine 30 (21-27 juillet 2025)
        date_cible = datetime(2025, 7, 21).date()
        lundi = date_cible - timedelta(days=date_cible.weekday())
        dimanche = lundi + timedelta(days=6)
        
        print(f"\n📅 Test pour la semaine {lundi.isocalendar()[1]} ({lundi} au {dimanche})")
        
        # Récupérer les interventions de cette semaine
        interventions = Intervention.query.filter(
            Intervention.date_planifiee >= lundi,
            Intervention.date_planifiee <= dimanche
        ).all()
        
        print(f"📊 Interventions trouvées: {len(interventions)}")
        for interv in interventions:
            print(f"  - Intervention {interv.id}: {interv.maintenance.titre} le {interv.date_planifiee}")
        
        # Calculer les maintenances qui devraient avoir des interventions cette semaine
        maintenances_semaine = []
        maintenances_actives = Maintenance.query.filter_by(active=True).all()
        
        for maintenance in maintenances_actives:
            try:
                if maintenance.date_premiere:
                    current_date = maintenance.date_premiere
                    while current_date <= dimanche:
                        if lundi <= current_date <= dimanche:
                            maintenances_semaine.append(maintenance)
                            break
                        # Calculer la prochaine date selon la périodicité
                        if maintenance.periodicite == 'semaine':
                            current_date += timedelta(days=7)
                        elif maintenance.periodicite == '2_semaines':
                            current_date += timedelta(days=14)
                        elif maintenance.periodicite == 'mois':
                            current_date += timedelta(days=30)
                        elif maintenance.periodicite == '2_mois':
                            current_date += timedelta(days=60)
                        elif maintenance.periodicite == '4_mois':
                            current_date += timedelta(days=120)
                        elif maintenance.periodicite == '6_mois':
                            current_date += timedelta(days=182)
                        elif maintenance.periodicite == '1_an':
                            current_date += timedelta(days=365)
                        elif maintenance.periodicite == '2_ans':
                            current_date += timedelta(days=730)
                        else:
                            break
                else:
                    # Si pas de date de première, inclure toutes les maintenances actives
                    maintenances_semaine.append(maintenance)
            except Exception as e:
                print(f"Erreur pour maintenance {maintenance.id}: {e}")
                maintenances_semaine.append(maintenance)
        
        print(f"\n📊 Maintenances calculées pour la semaine: {len(maintenances_semaine)}")
        for m in maintenances_semaine:
            equip = m.equipement.nom if m.equipement else 'N/A'
            print(f"  - {m.titre} (Équipement: {equip}, Périodicité: {m.periodicite})")

if __name__ == '__main__':
    test_database() 