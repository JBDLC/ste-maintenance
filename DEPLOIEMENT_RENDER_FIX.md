# 🔧 Guide de Déploiement Render.com - Correction des Erreurs

## ❌ Problème Identifié
L'erreur de compilation de `greenlet` et l'incompatibilité de `psycopg[binary]==3.1.13` sont dues à des versions incompatibles sur Render.com.

## ✅ Solutions Appliquées

### 1. **Version Python Stable**
- Changé de `python-3.12.0` vers `python-3.10.12`
- Python 3.10 est très stable et compatible avec toutes les dépendances

### 2. **Dépendances Fixées**
- `psycopg[binary]==3.2.9` (version disponible)
- `greenlet==3.0.1` (version compatible)
- Toutes les autres dépendances ont des versions fixes

### 3. **Configuration Render**
- Ajouté `render.yaml` pour la configuration automatique
- `Procfile` déjà correct

## 🚀 Étapes de Déploiement

### Étape 1 : Test Local
```bash
python test_deploy.py
```

### Étape 2 : Pousser les Changements
```bash
git add .
git commit -m "Fix: Compatibilité Render.com - Python 3.10 et psycopg 3.2.9"
git push origin main
```

### Étape 3 : Sur Render.com
1. **Connectez-vous** à votre dashboard Render.com
2. **Créez un nouveau service Web** (si pas déjà fait)
3. **Connectez votre repository Git**
4. **Configuration automatique** via `render.yaml`

### Étape 4 : Variables d'Environnement
Assurez-vous d'avoir ces variables sur Render.com :
```
DATABASE_URL=postgresql://...
SECRET_KEY=votre_clé_secrète
FLASK_ENV=production
```

## 🔍 Vérification

### Avant le Déploiement
- ✅ `runtime.txt` : `python-3.10.12`
- ✅ `requirements.txt` : versions fixes (psycopg 3.2.9)
- ✅ `render.yaml` : configuration présente
- ✅ `Procfile` : `web: gunicorn app:app --bind 0.0.0.0:$PORT`
- ✅ `test_deploy.py` : script de test créé

### Après le Déploiement
- ✅ Build réussi (plus d'erreur greenlet/psycopg)
- ✅ Application accessible
- ✅ Base de données connectée

## 🛠️ En Cas de Problème

### Si l'erreur persiste :
1. **Vérifiez les logs** dans le dashboard Render
2. **Redéployez** avec `git push`
3. **Contactez le support** si nécessaire

### Commandes Utiles
```bash
# Test local avant déploiement
python test_deploy.py

# Vérifier la configuration locale
python --version
pip list | grep -E "(greenlet|psycopg|Flask)"

# Tester localement
python app.py
```

## 📋 Résumé des Changements

| Fichier | Changement | Raison |
|---------|------------|---------|
| `runtime.txt` | Python 3.10.12 | Compatibilité maximale |
| `requirements.txt` | psycopg 3.2.9 | Version disponible |
| `render.yaml` | Python 3.10.12 | Configuration |
| `test_deploy.py` | Nouveau | Test pré-déploiement |
| `deploy.sh` | Mis à jour | Guide déploiement |

## ✅ Résultat Attendu
- ✅ Déploiement réussi sur Render.com
- ✅ Plus d'erreur de compilation greenlet/psycopg
- ✅ Application fonctionnelle avec rapport Excel
- ✅ Base de données PostgreSQL connectée

## 🧪 Test de Validation

Exécutez le script de test pour vérifier la compatibilité :
```bash
python test_deploy.py
```

Ce script vérifie :
- ✅ Tous les imports de dépendances
- ✅ Validité du requirements.txt
- ✅ Démarrage de l'application Flask

---
**Note** : Ces changements résolvent les problèmes de compatibilité tout en conservant toutes les fonctionnalités (rapport Excel avec 3 onglets, calendrier CO6/CO7, etc.) 