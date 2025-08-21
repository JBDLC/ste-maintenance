# Guide de Déploiement : Données Fournisseur sur Render

## 🚨 **Problème identifié**

L'erreur sur Render indique que la colonne `donnees_fournisseur` n'existe pas dans la base PostgreSQL :

```
sqlalchemy.exc.ProgrammingError: (psycopg.errors.UndefinedColumn) 
column piece.donnees_fournisseur does not exist
```

## ✅ **Solution implémentée**

### 1. **Migration automatique au démarrage**
- L'application détecte automatiquement PostgreSQL
- Ajoute la colonne `donnees_fournisseur` si elle n'existe pas
- S'exécute à chaque redémarrage de l'application

### 2. **Code de migration intégré**
```python
# Migration automatique pour PostgreSQL (donnees_fournisseur)
try:
    if 'postgresql' in str(db.engine.url):
        print("🔧 Détection PostgreSQL - Vérification de la colonne donnees_fournisseur...")
        
        # Vérifier si la colonne existe
        result = db.session.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur'
        """).fetchone()
        
        if not result:
            print("🔧 Ajout de la colonne donnees_fournisseur...")
            db.session.execute("""
                ALTER TABLE piece 
                ADD COLUMN donnees_fournisseur TEXT
            """)
            db.session.commit()
            print("✅ Colonne donnees_fournisseur ajoutée avec succès!")
        else:
            print("✅ Colonne donnees_fournisseur existe déjà")
    else:
        print("ℹ️ Base SQLite détectée - Migration non nécessaire")
        
except Exception as e:
    print(f"⚠️ Erreur lors de la migration PostgreSQL: {e}")
    # Ne pas faire échouer l'application pour une migration
    db.session.rollback()
```

## 🚀 **Déploiement sur Render**

### **Étape 1 : Redéployer l'application**
1. Pousser les modifications sur GitHub
2. Render redéploiera automatiquement
3. La migration s'exécutera au démarrage

### **Étape 2 : Vérifier les logs**
Dans les logs Render, vous devriez voir :
```
🔍 Initialisation de la base de données...
✅ Tables créées avec succès!
🔧 Détection PostgreSQL - Vérification de la colonne donnees_fournisseur...
🔧 Ajout de la colonne donnees_fournisseur...
✅ Colonne donnees_fournisseur ajoutée avec succès!
```

### **Étape 3 : Test de la fonctionnalité**
1. Aller sur `/pieces` → Plus d'erreur 500
2. Ajouter une pièce → Champ "Données fournisseur" disponible
3. Modifier une pièce → Champ pré-rempli

## 🔧 **Migration manuelle (si nécessaire)**

Si la migration automatique échoue, exécuter manuellement sur Render :

```sql
ALTER TABLE piece ADD COLUMN donnees_fournisseur TEXT;
```

## 📋 **Vérification de la migration**

### **Requête de vérification**
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur';
```

### **Résultat attendu**
```
column_name        | data_type
-------------------|----------
donnees_fournisseur| text
```

## 🎯 **Points clés**

- ✅ **Migration automatique** au démarrage
- ✅ **Détection PostgreSQL** vs SQLite
- ✅ **Gestion d'erreur** sans faire échouer l'app
- ✅ **Logs détaillés** pour le debugging
- ✅ **Rollback automatique** en cas d'erreur

## 🚨 **En cas de problème persistant**

1. **Vérifier les logs Render** pour les erreurs de migration
2. **Redémarrer l'application** pour relancer la migration
3. **Vérifier la connexion PostgreSQL** dans les variables d'environnement
4. **Exécuter la migration manuellement** si nécessaire

---

*Cette solution garantit que la colonne sera créée automatiquement sur tous les environnements PostgreSQL, y compris Render.* 