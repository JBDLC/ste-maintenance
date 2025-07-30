# Migration vers psycopg3

## Problème résolu

L'application rencontrait une erreur de déploiement sur Render avec Python 3.13 :

```
ImportError: /opt/render/project/src/.venv/lib/python3.13/site-packages/psycopg2/_psycopg.cpython-313-x86_64-linux-gnu.so: undefined symbol: _PyInterpreterState_Get
```

Cette erreur est due à l'incompatibilité entre `psycopg2` et Python 3.13.

## Solution appliquée

### 1. Mise à jour des dépendances

**Avant :**
```
psycopg2-binary==2.9.9
```

**Après :**
```
psycopg[binary]==3.2.9
```

### 2. Mise à jour de la configuration SQLAlchemy

**Avant :**
```python
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg2://', 1)
elif DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://', 1)
```

**Après :**
```python
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
elif DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
```

## Avantages de psycopg3

1. **Compatibilité Python 3.13** : Support complet de Python 3.13
2. **Performance améliorée** : Plus rapide que psycopg2
3. **API moderne** : Interface plus moderne et intuitive
4. **Support long terme** : Maintenance active et support futur

## Tests effectués

- ✅ Import de psycopg3
- ✅ Configuration SQLAlchemy avec psycopg3
- ✅ Import de l'application complète
- ✅ Fonctionnement local

## Déploiement

Le déploiement sur Render devrait maintenant fonctionner correctement avec Python 3.13 et psycopg3.

## Fichiers modifiés

- `requirements.txt` : Mise à jour de psycopg2 vers psycopg3
- `app.py` : Mise à jour de la configuration SQLAlchemy
- `test_psycopg3.py` : Fichier de test créé pour vérifier la compatibilité 