# Application de Gestion de Maintenance Préventive

Une application Flask complète pour la gestion de maintenance préventive avec gestion des sites, localisations, équipements, pièces de rechange et calendrier de maintenance.

## Fonctionnalités

### Gestion hiérarchique
- **Sites** : Création et gestion des sites
- **Localisations** : Localisations attachées aux sites
- **Équipements** : Équipements attachés aux localisations

### Maintenance préventive
- Création de tâches de maintenance avec périodicité configurable
- Périodicités disponibles : semaine, 2 semaines, mois, 2 mois, 6 mois, 1 an, 2 ans
- Calendrier hebdomadaire des maintenances à réaliser
- Suivi du statut des interventions (planifiée, réalisée, annulée)

### Gestion des pièces de rechange
- Catalogue complet des pièces avec références STE et magasin
- Gestion des stocks (quantité, minimum, maximum)
- Réapprovisionnement automatique
- Mouvements de stock (entrées/sorties)
- Association des pièces aux équipements

### Notifications
- Envoi automatique d'emails lors de la réalisation des maintenances
- Configuration email personnalisable

## Installation Locale

1. **Cloner le projet**
```bash
git clone <url-du-projet>
cd maintenance-ste
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration**
- Copier `env_example.txt` vers `.env`
- Modifier les variables dans `.env` :
  - `SECRET_KEY` : Clé secrète pour l'application
  - Configuration email (Gmail recommandé)

5. **Lancer l'application**
```bash
python app.py
```

L'application sera accessible à l'adresse : http://localhost:5000

## Déploiement sur Render

### Prérequis
- Compte GitHub
- Compte Render (gratuit)

### Étapes de déploiement

1. **Pousser sur GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/votre-username/maintenance-ste.git
git push -u origin main
```

2. **Déployer sur Render**
- Aller sur [render.com](https://render.com)
- Créer un compte et se connecter
- Cliquer sur "New +" → "Web Service"
- Connecter votre repository GitHub
- Configurer le service :
  - **Name** : maintenance-ste
  - **Environment** : Python
  - **Build Command** : `pip install -r requirements.txt`
  - **Start Command** : `gunicorn app:app`
  - **Plan** : Free

3. **Configurer la base de données PostgreSQL**
- Dans Render, aller dans "New +" → "PostgreSQL"
- Créer une base de données
- Copier l'URL de connexion
- Dans votre service web, ajouter la variable d'environnement :
  - **Key** : `DATABASE_URL`
  - **Value** : L'URL PostgreSQL copiée

4. **Variables d'environnement**
Dans votre service web, ajouter ces variables :
- `SECRET_KEY` : Une clé secrète aléatoire
- `MAIL_USERNAME` : Votre email Gmail
- `MAIL_PASSWORD` : Votre mot de passe d'application Gmail
- `MAIL_DEFAULT_SENDER` : Votre email Gmail

### Configuration Email pour la Production

1. **Gmail** (recommandé) :
   - Activer l'authentification à 2 facteurs
   - Générer un mot de passe d'application
   - Utiliser ce mot de passe dans `MAIL_PASSWORD`

2. **Autres fournisseurs** :
   - Modifier `MAIL_SERVER` et `MAIL_PORT` selon le fournisseur
   - Configurer les identifiants appropriés

## Structure de la base de données

### Sites
- Nom et description
- Contient plusieurs localisations

### Localisations
- Nom et description
- Appartient à un site
- Contient plusieurs équipements

### Équipements
- Nom et description
- Appartient à une localisation
- Peut avoir plusieurs maintenances
- Peut être associé à plusieurs pièces

### Pièces de rechange
- Référence STE (unique)
- Référence magasin
- Item et description
- Zone de stockage
- Gestion des stocks (actuel, minimum, maximum)

### Maintenances
- Titre et description
- Équipement associé
- Périodicité configurable
- Date de première maintenance
- Date de prochaine maintenance

### Interventions
- Maintenance associée
- Date planifiée et réalisée
- Statut (planifiée, réalisée, annulée)
- Commentaire
- Pièces utilisées

### Mouvements de pièces
- Pièce concernée
- Type (entrée/sortie)
- Quantité
- Date et motif
- Intervention associée (optionnel)

## Utilisation

### 1. Configuration initiale
1. Créer des sites
2. Ajouter des localisations pour chaque site
3. Créer des équipements dans les localisations
4. Ajouter des pièces de rechange au catalogue

### 2. Planification des maintenances
1. Créer des tâches de maintenance pour les équipements
2. Définir la périodicité et la date de première maintenance
3. Le système génère automatiquement le calendrier

### 3. Suivi hebdomadaire
1. Consulter le calendrier pour voir les maintenances de la semaine
2. Réaliser les interventions planifiées
3. Indiquer les pièces utilisées lors des interventions
4. Les emails de confirmation sont envoyés automatiquement

### 4. Gestion des stocks
1. Surveiller les niveaux de stock dans le catalogue des pièces
2. Réapprovisionner les pièces en rupture
3. Consulter l'historique des mouvements

## Développement

### Ajout de nouvelles fonctionnalités
- Les modèles sont dans `app.py`
- Les templates sont dans le dossier `templates/`
- Les routes sont définies dans `app.py`

### Base de données
- SQLite en développement (fichier `maintenance.db`)
- PostgreSQL en production (via Render)
- Modifier `SQLALCHEMY_DATABASE_URI` dans la configuration

## Support

Pour toute question ou problème, consulter la documentation ou créer une issue sur le repository. 