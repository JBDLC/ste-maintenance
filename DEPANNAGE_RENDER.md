# 🔧 Dépannage : Erreur Internal Server Error sur Render

## Problème
L'application démarre sur Render mais affiche "Internal Server Error" sur toutes les pages.

## Causes possibles

### 1. **Base de données PostgreSQL non initialisée** ✅ SOLUTION APPLIQUÉE
- Les tables n'existent pas dans PostgreSQL
- L'utilisateur admin n'est pas créé
- Erreur lors de l'initialisation

### 2. **Variables d'environnement manquantes**
- `DATABASE_URL` non configurée
- `SECRET_KEY` manquante

### 3. **Problème de connexion PostgreSQL**
- URL de connexion incorrecte
- Permissions insuffisantes

## ✅ Solutions appliquées

### 1. **Script d'initialisation corrigé**
- Créé `init_render.py` avec tous les modèles
- Gestion d'erreur améliorée dans `app.py`
- Fallback en cas d'échec d'initialisation

### 2. **Configuration PostgreSQL forcée**
- URL forcée : `postgresql+psycopg://` pour utiliser `psycopg3`
- Compatible avec Python 3.13 sur Render

### 3. **Scripts de diagnostic**
- `debug_render.py` : Test de connexion et création des tables
- `init_render.py` : Initialisation complète de la base

## 🔍 Diagnostic

### Étape 1 : Vérifier les variables d'environnement
Sur Render, vérifiez que vous avez configuré :
- `DATABASE_URL` : URL PostgreSQL complète
- `SECRET_KEY` : Clé secrète pour Flask

### Étape 2 : Vérifier les logs Render
1. Allez dans votre service sur Render
2. Cliquez sur "Logs"
3. Cherchez les erreurs d'initialisation

### Étape 3 : Tester la connexion
Utilisez le script de diagnostic :
```bash
python debug_render.py
```

## 🚀 Redéploiement

1. **Pousser les modifications** :
```bash
git add .
git commit -m "Fix: Initialisation PostgreSQL Render"
git push
```

2. **Vérifier les logs** sur Render après le redéploiement

3. **Tester l'application** :
- Aller sur votre URL Render
- Se connecter avec `admin` / `admin123`

## 📋 Identifiants par défaut

Si l'initialisation réussit, vous pourrez vous connecter avec :
- **Username** : `admin`
- **Password** : `admin123`

## 🔧 Commandes utiles

```bash
# Test local avec PostgreSQL
python debug_render.py

# Initialisation manuelle
python init_render.py

# Vérifier les variables d'environnement
echo $DATABASE_URL
echo $SECRET_KEY
```

## Support

Si le problème persiste :
1. Vérifiez les logs complets sur Render
2. Testez avec `debug_render.py`
3. Contactez le support Render si nécessaire 