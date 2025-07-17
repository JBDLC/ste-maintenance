# Guide de Déploiement - Maintenance STE

Ce guide vous accompagne pour déployer votre application de maintenance sur GitHub et Render avec PostgreSQL.

## 🚀 Étapes de Déploiement

### 1. Préparation du Repository GitHub

#### A. Initialiser Git (si pas déjà fait)
```bash
git init
git add .
git commit -m "Initial commit - Application de maintenance"
```

#### B. Créer un repository sur GitHub
1. Aller sur [github.com](https://github.com)
2. Cliquer sur "New repository"
3. Nommer le repository : `maintenance-ste`
4. Ne pas initialiser avec README (déjà présent)
5. Cliquer sur "Create repository"

#### C. Pousser le code
```bash
git branch -M main
git remote add origin https://github.com/VOTRE_USERNAME/maintenance-ste.git
git push -u origin main
```

### 2. Configuration Render

#### A. Créer un compte Render
1. Aller sur [render.com](https://render.com)
2. Créer un compte (gratuit)
3. Se connecter

#### B. Créer la base de données PostgreSQL
1. Dans le dashboard Render, cliquer sur "New +"
2. Sélectionner "PostgreSQL"
3. Configurer :
   - **Name** : `maintenance-db`
   - **Database** : `maintenance`
   - **User** : `maintenance_user`
   - **Plan** : Free
4. Cliquer sur "Create Database"
5. **IMPORTANT** : Copier l'URL de connexion (Internal Database URL)

#### C. Créer le service web
1. Cliquer sur "New +" → "Web Service"
2. Connecter votre repository GitHub
3. Configurer le service :
   - **Name** : `maintenance-ste`
   - **Environment** : Python
   - **Region** : Frankfurt (EU Central)
   - **Branch** : `main`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan** : Free

#### D. Configurer les variables d'environnement
Dans votre service web, aller dans "Environment" et ajouter :

**Variables obligatoires :**
- `DATABASE_URL` : L'URL PostgreSQL copiée précédemment
- `SECRET_KEY` : Une clé secrète aléatoire (ex: `your-super-secret-key-here`)

**Variables email (optionnelles) :**
- `MAIL_USERNAME` : Votre email Gmail
- `MAIL_PASSWORD` : Votre mot de passe d'application Gmail
- `MAIL_DEFAULT_SENDER` : Votre email Gmail

### 3. Configuration Email (Optionnel)

#### A. Gmail
1. Aller dans les paramètres de votre compte Gmail
2. Activer l'authentification à 2 facteurs
3. Générer un mot de passe d'application
4. Utiliser ce mot de passe dans `MAIL_PASSWORD`

#### B. Autres fournisseurs
- Modifier `MAIL_SERVER` et `MAIL_PORT` selon le fournisseur
- Configurer les identifiants appropriés

### 4. Déploiement

#### A. Déployer automatiquement
1. Render détecte automatiquement les changements sur GitHub
2. Chaque push sur `main` déclenche un nouveau déploiement
3. Suivre les logs dans l'onglet "Logs" de Render

#### B. Vérifier le déploiement
1. Aller dans l'onglet "Logs" de votre service
2. Vérifier qu'il n'y a pas d'erreurs
3. Cliquer sur l'URL fournie par Render
4. L'application devrait être accessible

### 5. Initialisation de la Base de Données

#### A. Première visite
1. Aller sur votre URL Render
2. L'application devrait créer automatiquement les tables
3. Si erreur, utiliser le script d'initialisation

#### B. Script d'initialisation (si nécessaire)
```bash
# En local, avec les variables d'environnement configurées
python init_db.py
```

### 6. Mise à Jour

#### A. Développement local
```bash
# Modifier le code
git add .
git commit -m "Description des changements"
git push origin main
```

#### B. Déploiement automatique
- Render détecte automatiquement les changements
- Le déploiement se fait en quelques minutes
- Vérifier les logs pour s'assurer du succès

## 🔧 Configuration Avancée

### Variables d'environnement disponibles

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `DATABASE_URL` | URL PostgreSQL | ✅ |
| `SECRET_KEY` | Clé secrète Flask | ✅ |
| `MAIL_USERNAME` | Email pour notifications | ❌ |
| `MAIL_PASSWORD` | Mot de passe email | ❌ |
| `MAIL_DEFAULT_SENDER` | Email expéditeur | ❌ |
| `MAIL_SERVER` | Serveur SMTP | ❌ |
| `MAIL_PORT` | Port SMTP | ❌ |
| `MAIL_USE_TLS` | Utiliser TLS | ❌ |

### Logs et Debugging

#### A. Voir les logs Render
1. Aller dans votre service web
2. Onglet "Logs"
3. Filtrer par niveau (Error, Warning, Info)

#### B. Debugging local avec PostgreSQL
```bash
# Installer PostgreSQL localement
# Configurer DATABASE_URL dans .env
python app.py
```

## 🚨 Dépannage

### Erreurs courantes

#### A. "Database connection failed"
- Vérifier que `DATABASE_URL` est correcte
- Vérifier que la base PostgreSQL est active
- Attendre quelques minutes après la création de la base

#### B. "Module not found"
- Vérifier que `requirements.txt` est à jour
- Vérifier les logs de build dans Render

#### C. "500 Internal Server Error"
- Vérifier les logs dans Render
- Vérifier la configuration des variables d'environnement

### Support

- **Logs Render** : Onglet "Logs" dans votre service
- **Documentation Render** : [docs.render.com](https://docs.render.com)
- **Issues GitHub** : Créer une issue sur votre repository

## 📊 Monitoring

### Métriques disponibles
- **Uptime** : Disponibilité du service
- **Logs** : Activité de l'application
- **Base de données** : Utilisation PostgreSQL

### Alertes
- Render envoie des alertes en cas de problème
- Vérifier régulièrement les logs

## 🔒 Sécurité

### Bonnes pratiques
- Ne jamais commiter de secrets dans Git
- Utiliser des variables d'environnement
- Changer régulièrement `SECRET_KEY`
- Utiliser HTTPS (automatique sur Render)

### Variables sensibles
- `SECRET_KEY` : Générer une clé aléatoire
- `DATABASE_URL` : Garder confidentielle
- `MAIL_PASSWORD` : Utiliser un mot de passe d'application

---

**🎉 Votre application est maintenant déployée et accessible en ligne !** 