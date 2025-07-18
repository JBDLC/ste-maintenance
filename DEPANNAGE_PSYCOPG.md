# Dépannage : Erreur psycopg2 avec Python 3.13

## Problème
L'erreur suivante se produit lors du déploiement sur Render :
```
ImportError: /opt/render/project/src/.venv/lib/python3.13/site-packages/psycopg2/_psycopg.cpython-313-x86_64-linux-gnu.so: undefined symbol: _PyInterpreterState_Get
```

## Cause
`psycopg2-binary` n'est pas encore compatible avec Python 3.13 sur Render.

## Solutions

### Solution 1 : Utiliser Python 3.12 (Recommandée)
Le fichier `runtime.txt` a été mis à jour pour utiliser Python 3.12 qui est compatible avec `psycopg2-binary`.

### Solution 2 : Migrer vers psycopg3
Si le problème persiste, remplacez `requirements.txt` par `requirements_psycopg3.txt` :

```bash
# Sur Render, dans les variables d'environnement :
# Ajoutez : REQUIREMENTS_FILE=requirements_psycopg3.txt
```

### Solution 3 : Forcer Python 3.11
Si nécessaire, revenez à Python 3.11 en modifiant `runtime.txt` :
```
python-3.11.0
```

## Vérification

1. **Test local** : Exécutez `python test_psycopg.py` pour vérifier la compatibilité
2. **Redéploiement** : Après modification, redéployez sur Render
3. **Logs** : Vérifiez les logs de déploiement sur Render

## Variables d'environnement Render

Assurez-vous d'avoir configuré :
- `DATABASE_URL` : URL de votre base PostgreSQL
- `SECRET_KEY` : Clé secrète pour Flask
- `REQUIREMENTS_FILE` : `requirements_psycopg3.txt` (si migration vers psycopg3)

## Commandes utiles

```bash
# Test local avec Python 3.12
python test_psycopg.py

# Vérifier la version de Python
python --version

# Installer les dépendances
pip install -r requirements.txt
```

## Support

Si le problème persiste :
1. Vérifiez les logs complets sur Render
2. Testez avec `psycopg3` en utilisant `requirements_psycopg3.txt`
3. Contactez le support Render si nécessaire 