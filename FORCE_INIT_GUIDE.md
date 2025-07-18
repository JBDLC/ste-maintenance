# 🔧 Guide : Forcer l'initialisation de PostgreSQL sur Render

## Problème identifié
L'erreur SQL montre que la table `user` n'existe pas dans PostgreSQL :
```
[SQL: SELECT "user".id AS user_id, "user".username AS user_username...]
```

## Solution : Initialisation forcée

### Étape 1 : Exécuter le script d'initialisation forcée

Sur Render, vous devez exécuter le script `force_init_db.py` pour créer toutes les tables :

1. **Allez dans votre service sur Render**
2. **Cliquez sur "Shell"** (ou utilisez la console)
3. **Exécutez la commande** :
```bash
python force_init_db.py
```

### Étape 2 : Vérifier l'exécution

Le script va :
- ✅ Supprimer toutes les tables existantes
- ✅ Recréer toutes les tables avec les bons noms
- ✅ Créer l'utilisateur admin
- ✅ Créer toutes les permissions

### Étape 3 : Tester l'application

Après l'exécution, testez l'application :
- **URL** : Votre URL Render
- **Username** : `admin`
- **Password** : `admin123`

## 🔍 Diagnostic

Si le script échoue, vérifiez :

1. **Variables d'environnement** :
   - `DATABASE_URL` est configurée
   - `SECRET_KEY` est configurée

2. **Logs Render** :
   - Allez dans "Logs" de votre service
   - Cherchez les erreurs d'exécution

3. **Connexion PostgreSQL** :
   - Vérifiez que la base PostgreSQL est active
   - Vérifiez les permissions de connexion

## 🚀 Alternative : Redéploiement avec initialisation

Si vous ne pouvez pas exécuter le script directement, modifiez temporairement `app.py` :

```python
if __name__ == '__main__':
    with app.app_context():
        # FORCER L'INITIALISATION
        db.drop_all()  # Supprimer toutes les tables
        db.create_all()  # Recréer toutes les tables
        
        # Créer l'admin
        admin = User(username='admin', password_hash=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
        
        # Créer les permissions
        pages = ['sites', 'localisations', 'equipements', 'pieces', 'lieux_stockage', 
                 'maintenances', 'calendrier', 'mouvements', 'parametres']
        
        for page in pages:
            permission = UserPermission(user_id=admin.id, page=page, can_access=True)
            db.session.add(permission)
        
        db.session.commit()
        print("✅ Base de données initialisée!")
    
    app.run(debug=True)
```

Puis redéployez et retirez ces modifications après le premier démarrage.

## 📋 Vérification

Après l'initialisation, vérifiez que :

1. **L'application démarre** sans erreur
2. **Vous pouvez vous connecter** avec admin/admin123
3. **Toutes les pages** fonctionnent
4. **Les tables existent** dans PostgreSQL

## 🔧 Commandes utiles

```bash
# Vérifier les tables PostgreSQL
python debug_render.py

# Forcer l'initialisation
python force_init_db.py

# Tester la connexion
python -c "from app import app, db; app.app_context().push(); print('Connexion OK')"
```

## Support

Si le problème persiste :
1. Vérifiez les logs complets sur Render
2. Testez la connexion PostgreSQL directement
3. Contactez le support Render si nécessaire 