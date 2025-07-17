# 🧑‍💼 Système de Gestion des Utilisateurs

## ✅ Fonctionnalités Implémentées

### **1. Modèles de Données**
- **User** : Utilisateurs avec email, mot de passe, statut actif
- **UserPermission** : Permissions granulaires par page et action

### **2. Tableau des Permissions**
- **Utilisateurs en lignes** : Liste de tous les utilisateurs actifs
- **Pages en colonnes** : Sites, Localisations, Équipements, Pièces, etc.
- **Actions par page** : Voir (V), Créer (C), Éditer (E), Supprimer (D)

### **3. Gestion des Utilisateurs**
- ✅ **Créer** un nouvel utilisateur
- ✅ **Supprimer** un utilisateur (désactivation)
- ✅ **Réinitialiser** le mot de passe
- ✅ **Modifier** les permissions en temps réel

### **4. Permissions Granulaires**
- **Voir** : Accès en lecture seule
- **Créer** : Ajouter de nouveaux éléments
- **Éditer** : Modifier les éléments existants
- **Supprimer** : Supprimer des éléments

## 🎯 Pages Gérées

| Page | Description | Permissions |
|------|-------------|-------------|
| **Sites** | Gestion des sites | V, C, E, D |
| **Localisations** | Gestion des localisations | V, C, E, D |
| **Équipements** | Gestion des équipements | V, C, E, D |
| **Pièces** | Gestion des pièces de rechange | V, C, E, D |
| **Lieux Stockage** | Gestion des lieux de stockage | V, C, E, D |
| **Maintenances** | Gestion des maintenances | V, C, E, D |
| **Calendrier** | Accès au calendrier | V, C, E, D |
| **Mouvements** | Gestion des mouvements de stock | V, C, E, D |
| **Paramètres** | Accès aux paramètres | V, C, E, D |

## 🚀 Utilisation

### **1. Accès à la Gestion**
1. Aller dans **Paramètres**
2. Cliquer sur **"Gestion Utilisateurs"**

### **2. Créer un Utilisateur**
1. Cliquer sur **"Nouvel Utilisateur"**
2. Remplir :
   - **Nom d'utilisateur** : Identifiant unique
   - **Email** : Adresse email
   - **Mot de passe** : Mot de passe initial
3. Cliquer sur **"Créer"**

### **3. Gérer les Permissions**
1. Dans le tableau, cocher/décocher les cases selon les droits souhaités
2. Les modifications sont **automatiquement sauvegardées**
3. **V** = Voir, **C** = Créer, **E** = Éditer, **D** = Supprimer

### **4. Actions sur les Utilisateurs**
- **🔑 Réinitialiser mot de passe** : Bouton clé
- **🗑️ Supprimer** : Bouton poubelle (impossible sur son propre compte)

## 🔧 Configuration Initiale

### **Créer un Administrateur**
```bash
python create_admin.py
```

**Identifiants par défaut :**
- **Utilisateur** : `admin`
- **Email** : `admin@maintenance-ste.com`
- **Mot de passe** : `admin123`

### **⚠️ Sécurité**
- **Changer le mot de passe admin** après la première connexion
- **Créer des utilisateurs** avec des permissions limitées
- **Ne pas partager** les identifiants admin

## 📊 Exemples de Profils

### **Administrateur**
- **Tous les droits** sur toutes les pages
- **Gestion des utilisateurs**
- **Configuration système**

### **Technicien**
- **Voir** : Sites, Localisations, Équipements, Pièces
- **Créer/Éditer** : Maintenances, Calendrier, Mouvements
- **Pas de suppression** ni accès aux paramètres

### **Observateur**
- **Voir uniquement** : Sites, Localisations, Équipements, Calendrier
- **Aucune modification** possible
- **Lecture seule**

### **Gestionnaire Stock**
- **Voir** : Sites, Localisations, Équipements
- **Créer/Éditer** : Pièces, Lieux Stockage, Mouvements
- **Pas d'accès** aux maintenances

## 🔒 Sécurité

### **Bonnes Pratiques**
- ✅ **Permissions minimales** : Donner le minimum de droits nécessaires
- ✅ **Comptes séparés** : Un compte par personne
- ✅ **Mots de passe forts** : Utiliser des mots de passe complexes
- ✅ **Révision régulière** : Vérifier les permissions périodiquement

### **Fonctionnalités de Sécurité**
- 🔒 **Empêche la suppression** de son propre compte
- 🔒 **Permissions granulaires** par action
- 🔒 **Validation côté serveur** de toutes les permissions
- 🔒 **Historique des modifications** (à implémenter)

## 🎯 Prochaines Améliorations

### **Fonctionnalités Avancées**
- 📊 **Historique des connexions**
- 📊 **Logs des actions** utilisateur
- 📊 **Groupes de permissions** (rôles)
- 📊 **Expiration des mots de passe**
- 📊 **Authentification à 2 facteurs**

### **Interface Améliorée**
- 🎨 **Filtres** par type de permission
- 🎨 **Recherche** d'utilisateurs
- 🎨 **Import/Export** des utilisateurs
- 🎨 **Copie de permissions** entre utilisateurs

---

**🎉 Le système de gestion des utilisateurs est maintenant opérationnel !** 