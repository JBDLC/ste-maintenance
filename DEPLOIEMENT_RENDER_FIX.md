# 🔧 Guide de Déploiement Render.com - Correction des Erreurs

## ❌ Problème Identifié
L'erreur de compilation de `greenlet` est due à une incompatibilité entre Python 3.12 et les dépendances sur Render.com.

## ✅ Solutions Appliquées

### 1. **Version Python Stable**
- Changé de `python-3.12.0` vers `python-3.11.7`
- Python 3.11 est plus stable et compatible avec les dépendances

### 2. **Dépendances Fixées**
- `psycopg[binary]==3.1.13` (version spécifique)
- `greenlet==3.0.1` (version compatible)
- Toutes les autres dépendances ont des versions fixes

### 3. **Configuration Render**
- Ajouté `render.yaml` pour la configuration automatique
- `Procfile` déjà correct

## 🚀 Étapes de Déploiement

### Étape 1 : Pousser les Changements
```bash
git add .
git commit -m "Fix: Compatibilité Render.com - Python 3.11 et dépendances fixes"
git push origin main
```

### Étape 2 : Sur Render.com
1. **Connectez-vous** à votre dashboard Render.com
2. **Créez un nouveau service Web** (si pas déjà fait)
3. **Connectez votre repository Git**
4. **Configuration automatique** via `render.yaml`

### Étape 3 : Variables d'Environnement
Assurez-vous d'avoir ces variables sur Render.com :
```
DATABASE_URL=postgresql://...
SECRET_KEY=votre_clé_secrète
FLASK_ENV=production
```

## 🔍 Vérification

### Avant le Déploiement
- ✅ `runtime.txt` : `python-3.11.7`
- ✅ `requirements.txt` : versions fixes
- ✅ `render.yaml` : configuration présente
- ✅ `Procfile` : `web: gunicorn app:app --bind 0.0.0.0:$PORT`

### Après le Déploiement
- ✅ Build réussi (plus d'erreur greenlet)
- ✅ Application accessible
- ✅ Base de données connectée

## 🛠️ En Cas de Problème

### Si l'erreur persiste :
1. **Vérifiez les logs** dans le dashboard Render
2. **Redéployez** avec `git push`
3. **Contactez le support** si nécessaire

### Commandes Utiles
```bash
# Vérifier la configuration locale
python --version
pip list | grep -E "(greenlet|psycopg|Flask)"

# Tester localement
python app.py
```

## 📋 Résumé des Changements

| Fichier | Changement | Raison |
|---------|------------|---------|
| `runtime.txt` | Python 3.11.7 | Compatibilité |
| `requirements.txt` | Versions fixes | Stabilité |
| `render.yaml` | Nouveau | Configuration |
| `deploy.sh` | Mis à jour | Guide déploiement |

## ✅ Résultat Attendu
- ✅ Déploiement réussi sur Render.com
- ✅ Plus d'erreur de compilation greenlet
- ✅ Application fonctionnelle avec rapport Excel
- ✅ Base de données PostgreSQL connectée

---
**Note** : Ces changements résolvent les problèmes de compatibilité tout en conservant toutes les fonctionnalités (rapport Excel avec 3 onglets, calendrier CO6/CO7, etc.) 