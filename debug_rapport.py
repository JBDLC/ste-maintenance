#!/usr/bin/env python3
"""
Script de debug pour vérifier les données de maintenance et interventions
"""

from app import app, db, Maintenance, Intervention, Equipement
from datetime import datetime, timedelta

def debug_rapport():
    with app.app_context():
        print("🔍 DEBUG - Vérification des données de maintenance")
        
        # Date de la semaine 30 (21-27 juillet 2025)
        date_cible = datetime(2025, 7, 21).date()
        lundi = date_cible - timedelta(days=date_cible.weekday())
        dimanche = lundi + timedelta(days=6)
        
        print(f"📅 Semaine {lundi.isocalendar()[1]}: {lundi} au {dimanche}")
        
        # Vérifier les maintenances
        maintenances = Maintenance.query.all()
        print(f"📋 {len(maintenances)} maintenances totales:")
        for m in maintenances:
            equip = m.equipement.nom if m.equipement else 'N/A'
            print(f"  - {m.titre} (Équipement: {equip}, Active: {m.active})")
        
        # Vérifier les interventions
        interventions = Intervention.query.filter(
            Intervention.date_planifiee >= lundi,
            Intervention.date_planifiee <= dimanche
        ).all()
        
        print(f"📋 {len(interventions)} interventions pour la semaine {lundi.isocalendar()[1]}:")
        for i in interventions:
            maint = i.maintenance.titre if i.maintenance else 'N/A'
            equip = i.maintenance.equipement.nom if i.maintenance and i.maintenance.equipement else 'N/A'
            print(f"  - {maint} (Équipement: {equip}, Date: {i.date_planifiee}, Statut: {i.statut})")
        
        # Vérifier toutes les interventions
        toutes_interventions = Intervention.query.all()
        print(f"📋 {len(toutes_interventions)} interventions totales:")
        for i in toutes_interventions[:10]:  # Afficher les 10 premières
            maint = i.maintenance.titre if i.maintenance else 'N/A'
            print(f"  - {maint} (Date: {i.date_planifiee}, Statut: {i.statut})")
        
        if len(toutes_interventions) > 10:
            print(f"  ... et {len(toutes_interventions) - 10} autres")

if __name__ == "__main__":
    debug_rapport() 