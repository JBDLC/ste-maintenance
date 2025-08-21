# 🗄️ Guide : Export Complet de la Base de Données

## 🎯 **Objectif**

Permettre l'export complet de votre base de données PostgreSQL depuis Render, directement depuis l'interface de l'application.

## 📍 **Où trouver cette fonctionnalité**

1. Aller dans **Paramètres** (icône ⚙️)
2. Descendre jusqu'à la section **"Export Complet de la Base de Données"**
3. Section avec fond rouge et icône de base de données

## 🚀 **Fonctionnalités disponibles**

### **1. Export Complet SQL** 🔴
- **Bouton principal** : Export Complet SQL
- **Format** : Fichier `.sql`
- **Contenu** : Structure + données de TOUTES les tables
- **Usage** : Sauvegarde complète, migration, restauration

### **2. Export Tables CSV** 📊
- **Bouton dropdown** : Export Tables CSV
- **Format** : Fichiers `.csv` séparés
- **Contenu** : Données d'une table spécifique
- **Usage** : Analyse Excel, import dans d'autres outils

## 📋 **Tables disponibles pour l'export CSV**

- **Sites** : Liste des sites
- **Localisations** : Localisations par site
- **Équipements** : Tous les équipements
- **Pièces** : Catalogue des pièces de rechange
- **Maintenances** : Planification des maintenances
- **Interventions** : Interventions réalisées
- **Mouvements Pièces** : Historique des mouvements
- **Utilisateurs** : Liste des utilisateurs

## 🔧 **Comment ça fonctionne**

### **Détection automatique**
- L'application détecte automatiquement si vous êtes sur :
  - **PostgreSQL** (Render) → Export optimisé PostgreSQL
  - **SQLite** (locale) → Export optimisé SQLite

### **Export PostgreSQL (Render)**
1. **Connexion** via `DATABASE_URL`
2. **Récupération** de la liste des tables
3. **Structure** : `CREATE TABLE` avec contraintes
4. **Données** : `INSERT` pour chaque ligne
5. **Fichier** : Script SQL exécutable

### **Export SQLite (Locale)**
1. **Connexion** directe au fichier `.db`
2. **Structure** : `PRAGMA table_info`
3. **Données** : Export ligne par ligne
4. **Fichier** : Script SQL compatible

## 📁 **Fichiers générés**

### **Export SQL complet**
```
export_base_complete_20250821_143022.sql
├── Structure des tables
├── Données de toutes les tables
└── Script exécutable
```

### **Export CSV par table**
```
piece_20250821_143022.csv
├── En-têtes des colonnes
├── Données de la table
└── Format Excel compatible
```

## 🎯 **Cas d'usage**

### **1. Sauvegarde avant migration**
- Exporter la base complète
- Effectuer les modifications
- Restaurer si nécessaire

### **2. Récupération depuis Render**
- Export complet depuis l'interface
- Téléchargement du fichier SQL
- Import dans un autre environnement

### **3. Analyse des données**
- Export CSV des tables importantes
- Ouverture dans Excel/Google Sheets
- Création de rapports personnalisés

### **4. Transfert d'environnement**
- Export depuis Render (PostgreSQL)
- Import vers SQLite local
- Ou vers un autre serveur PostgreSQL

## ⚠️ **Précautions importantes**

### **Sécurité**
- ✅ **Authentification requise** : Seuls les utilisateurs connectés
- ✅ **Permissions** : Vérification des droits d'accès
- ✅ **Validation** : Vérification de l'existence des tables

### **Performance**
- ⚠️ **Temps d'export** : Peut prendre du temps pour de grosses bases
- ⚠️ **Taille des fichiers** : Peut être volumineux
- ⚠️ **Mémoire** : Utilisation temporaire de la RAM

### **Limitations**
- 🔒 **Tables système** : Exclues (PostgreSQL)
- 🔒 **Vues** : Non exportées
- 🔒 **Procédures stockées** : Non exportées

## 🚨 **En cas de problème**

### **Erreur de connexion**
- Vérifier la variable `DATABASE_URL` sur Render
- Contrôler les permissions de la base
- Vérifier la connectivité réseau

### **Erreur d'export**
- Contrôler les logs de l'application
- Vérifier l'espace disque disponible
- Contrôler les permissions d'écriture

### **Fichier corrompu**
- Relancer l'export
- Vérifier la taille du fichier
- Tester l'ouverture du fichier

## 💡 **Conseils d'utilisation**

### **Pour la sauvegarde**
- **Fréquence** : Avant chaque déploiement majeur
- **Format** : Préférer l'export SQL complet
- **Stockage** : Sauvegarder dans un endroit sûr

### **Pour l'analyse**
- **Format** : Préférer l'export CSV par table
- **Tables** : Exporter seulement les tables nécessaires
- **Traitement** : Utiliser Excel ou des outils d'analyse

### **Pour la migration**
- **Format** : Export SQL complet obligatoire
- **Vérification** : Tester l'import sur l'environnement cible
- **Rollback** : Garder une copie de l'ancienne base

---

**🎉 Cette fonctionnalité vous donne un contrôle total sur vos données, même depuis Render !** 