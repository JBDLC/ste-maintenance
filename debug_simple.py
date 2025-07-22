#!/usr/bin/env python3
"""
Script de debug simple pour vérifier les données
"""

import sqlite3
from datetime import datetime, timedelta

def debug_simple():
    # Connexion à la base SQLite
    conn = sqlite3.connect('instance/maintenance.db')
    cursor = conn.cursor()
    
    print("🔍 DEBUG - Vérification des données de maintenance")
    
    # Date de la semaine 30 (21-27 juillet 2025)
    date_cible = datetime(2025, 7, 21).date()
    lundi = date_cible - timedelta(days=date_cible.weekday())
    dimanche = lundi + timedelta(days=6)
    
    print(f"📅 Semaine {lundi.isocalendar()[1]}: {lundi} au {dimanche}")
    
    # Vérifier les maintenances
    cursor.execute("SELECT id, titre, equipement_id, active FROM maintenance")
    maintenances = cursor.fetchall()
    print(f"📋 {len(maintenances)} maintenances totales:")
    for m in maintenances:
        print(f"  - ID: {m[0]}, Titre: {m[1]}, Équipement: {m[2]}, Active: {m[3]}")
    
    # Vérifier les interventions
    cursor.execute("""
        SELECT id, maintenance_id, date_planifiee, statut 
        FROM intervention 
        WHERE date_planifiee >= ? AND date_planifiee <= ?
    """, (lundi, dimanche))
    interventions = cursor.fetchall()
    
    print(f"📋 {len(interventions)} interventions pour la semaine {lundi.isocalendar()[1]}:")
    for i in interventions:
        print(f"  - ID: {i[0]}, Maintenance: {i[1]}, Date: {i[2]}, Statut: {i[3]}")
    
    # Vérifier toutes les interventions
    cursor.execute("SELECT id, maintenance_id, date_planifiee, statut FROM intervention LIMIT 10")
    toutes_interventions = cursor.fetchall()
    print(f"📋 {len(toutes_interventions)} premières interventions:")
    for i in toutes_interventions:
        print(f"  - ID: {i[0]}, Maintenance: {i[1]}, Date: {i[2]}, Statut: {i[3]}")
    
    conn.close()

if __name__ == "__main__":
    debug_simple() 