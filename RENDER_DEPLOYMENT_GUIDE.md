# Guide de déploiement Render avec PostgreSQL

## 🎯 **Objectif**
Déployer votre application Flask avec PostgreSQL sur Render sans perdre les données à chaque déploiement.

## 📋 **Étapes de configuration**

### **1. Configuration de la base PostgreSQL sur Render**

1. **Allez sur votre dashboard Render**
2. **Créez une nouvelle base PostgreSQL** :
   - Cliquez sur "New" → "PostgreSQL"
   - Donnez un nom à votre base (ex: `maintenance-db`)
   - Choisissez le plan gratuit
   - Cliquez sur "Create Database"

3. **Récupérez les informations de connexion** :
   - Notez l'URL de connexion (ex: `postgresql://user:password@host:port/database`)
   - Cette URL sera votre `DATABASE_URL`

### **2. Configuration de votre service web**

1. **Dans votre service web sur Render** :
   - Allez dans "Environment"
   - Ajoutez la variable d'environnement :
     - **Clé** : `DATABASE_URL`
     - **Valeur** : L'URL PostgreSQL de l'étape précédente

2. **Vérifiez que ces variables sont configurées** :
   - `DATABASE_URL` : URL de votre base PostgreSQL
   - `SECRET_KEY` : Clé secrète (générée automatiquement par Render)

### **3. Configuration du build**

Votre `render.yaml` est déjà configuré correctement :
```yaml
services:
  - type: web
    name: maintenance-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        generateValue: true
```

## 🔍 **Vérification du déploiement**

### **Après le déploiement, vérifiez :**

1. **Les logs de déploiement** :
   - Allez dans "Logs" de votre service
   - Vérifiez qu'il n'y a pas d'erreurs
   - Cherchez les messages d'initialisation de la base

2. **Testez l'application** :
   - Allez sur l'URL de votre application
   - Essayez de vous connecter avec `admin` / `admin123`
   - Vérifiez que les données persistent entre les déploiements

3. **Vérifiez la base de données** :
   - Dans votre dashboard PostgreSQL sur Render
   - Vérifiez que les tables sont créées
   - Vérifiez que l'utilisateur admin existe

## 🛠️ **Scripts de vérification**

### **Localement (pour tester) :**
```bash
python check_db.py
```

### **Sur Render (après déploiement) :**
Les logs de Render montreront les messages d'initialisation.

## 🔧 **Résolution des problèmes**

### **Problème : "DATABASE_URL non configurée"**
**Solution** : Vérifiez que la variable d'environnement est bien configurée dans votre service Render.

### **Problème : "Connexion PostgreSQL échouée"**
**Solution** : 
1. Vérifiez l'URL de connexion
2. Assurez-vous que la base PostgreSQL est active
3. Vérifiez que les dépendances PostgreSQL sont installées

### **Problème : "Tables non créées"**
**Solution** : Le script `render_init.py` s'exécute automatiquement au démarrage pour créer les tables.

## 📊 **Monitoring**

### **Vérifiez régulièrement :**
- Les logs de déploiement
- L'état de votre base PostgreSQL
- Les performances de l'application
- Les sauvegardes automatiques de Render

## ✅ **Checklist de déploiement**

- [ ] Base PostgreSQL créée sur Render
- [ ] Variable `DATABASE_URL` configurée
- [ ] Variable `SECRET_KEY` configurée
- [ ] Déploiement réussi
- [ ] Application accessible
- [ ] Connexion admin fonctionne
- [ ] Données persistent entre déploiements

## 🎉 **Résultat attendu**

Après configuration, votre application :
- ✅ Se connecte automatiquement à PostgreSQL
- ✅ Crée les tables au premier démarrage
- ✅ Crée l'utilisateur admin automatiquement
- ✅ Conserve les données entre les déploiements
- ✅ Fonctionne de manière stable 