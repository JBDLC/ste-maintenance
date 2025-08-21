# 🚨 Résolution Rapide : Erreur Migration PostgreSQL

## ⚠️ **Problème identifié**

La migration automatique a échoué à cause d'une erreur SQLAlchemy 2.0+ :
```
⚠️ Erreur lors de la migration PostgreSQL: Textual SQL expression should be explicitly declared as text()
```

## ✅ **Solution 1 : Redéploiement automatique (recommandé)**

1. **Pousser les corrections** sur GitHub
2. **Render redéploiera automatiquement**
3. **La migration corrigée s'exécutera**

## 🔧 **Solution 2 : Migration manuelle (si urgent)**

### **Étape 1 : Connexion SSH à Render**
```bash
# Dans le terminal Render ou via SSH
cd /opt/render/project/src
```

### **Étape 2 : Exécuter la migration manuelle**
```bash
python migrate_postgresql_manual.py
```

### **Étape 3 : Vérifier le résultat**
```bash
# Vérifier que la colonne existe
psql $DATABASE_URL -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur';
"
```

## 🎯 **Solution 3 : Requête SQL directe**

Si tout échoue, exécuter directement en base :

```sql
-- Vérifier si la colonne existe
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur';

-- Ajouter la colonne si elle n'existe pas
ALTER TABLE piece ADD COLUMN donnees_fournisseur TEXT;

-- Vérifier l'ajout
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'piece' AND column_name = 'donnees_fournisseur';
```

## 📋 **Vérification de la résolution**

### **Test 1 : Page /pieces**
- ✅ Plus d'erreur 500
- ✅ Liste des pièces s'affiche

### **Test 2 : Ajout de pièce**
- ✅ Champ "Données fournisseur" visible
- ✅ Sauvegarde fonctionne

### **Test 3 : Modification de pièce**
- ✅ Champ pré-rempli
- ✅ Mise à jour fonctionne

## 🚀 **Ordre de priorité**

1. **🔥 URGENT** : Solution 2 (migration manuelle)
2. **⚡ RAPIDE** : Solution 3 (SQL direct)
3. **🔄 AUTOMATIQUE** : Solution 1 (redéploiement)

## 💡 **Pourquoi cette erreur ?**

- **SQLAlchemy 2.0+** exige `text()` pour les requêtes SQL brutes
- **Ancienne syntaxe** : `db.session.execute("SELECT...")`
- **Nouvelle syntaxe** : `db.session.execute(text("SELECT..."))`

## ✅ **Correction appliquée**

```python
from sqlalchemy import text

# Avant (erreur)
result = db.session.execute("""
    SELECT column_name FROM information_schema.columns...
""").fetchone()

# Après (correct)
result = db.session.execute(text("""
    SELECT column_name FROM information_schema.columns...
""")).fetchone()
```

---

**🎯 Objectif : Résoudre l'erreur 500 sur /pieces en ajoutant la colonne donnees_fournisseur** 