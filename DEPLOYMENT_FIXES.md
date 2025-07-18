# Corrections pour le déploiement Render

## Problème identifié
Le déploiement sur Render échouait à cause de la compilation de `pandas` qui nécessite Cython et des outils de compilation qui ne sont pas disponibles sur l'environnement de build de Render.

## Solutions appliquées

### 1. Remplacement de pandas par des alternatives légères
- **Supprimé** : `pandas==2.1.4` du `requirements.txt`
- **Ajouté** : `xlrd==2.0.1` pour la lecture de fichiers Excel
- **Utilisé** : `openpyxl` (déjà présent) pour l'écriture de fichiers Excel
- **Utilisé** : `csv` (module standard Python) pour la lecture/écriture de fichiers CSV

### 2. Nouvelles fonctions utilitaires
Créées dans `app.py` pour remplacer pandas :

- `create_dataframe()` : Crée une structure de données similaire à un DataFrame
- `is_na()` : Vérifie si une valeur est NaN (remplace `pd.isna`)
- `read_excel_simple()` : Lit un fichier Excel (remplace `pd.read_excel`)
- `write_excel_simple()` : Écrit un fichier Excel (remplace `pd.ExcelWriter`)
- `read_csv_simple()` : Lit un fichier CSV (remplace `pd.read_csv`)

### 3. Modifications des fonctions d'import/export
- `download_modele()` : Utilise maintenant `write_excel_simple()` et `csv.DictWriter`
- `download_modele_maintenances()` : Utilise `openpyxl` directement
- `export_donnees()` : Utilise `openpyxl` pour créer des fichiers Excel multi-onglets
- `import_donnees()` : Utilise `read_excel_simple()` et `read_csv_simple()`

### 4. Migration des données
- `migrations.py` : Remplace pandas par `csv` et `sqlite3` pour l'export/import

### 5. Configuration Render
- `render.yaml` : Configuration optimisée pour Render
- `runtime.txt` : Version Python 3.11.0
- `Procfile` : Commande de démarrage pour Render

## Avantages
1. **Déploiement plus rapide** : Pas de compilation Cython
2. **Moins de dépendances** : Suppression de pandas et ses dépendances
3. **Plus léger** : Application plus petite et plus rapide
4. **Compatibilité** : Fonctionne sur tous les environnements

## Test local
L'application s'importe correctement et toutes les fonctionnalités d'import/export sont préservées.

## Déploiement
1. Commitez ces changements
2. Poussez vers votre repository
3. Redéployez sur Render
4. L'application devrait maintenant se déployer sans erreur 