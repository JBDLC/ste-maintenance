# Guide d'utilisation - Modification des maintenances curatives

## 🎯 Fonctionnalité ajoutée

La fonctionnalité de **modification des maintenances curatives** permet de corriger ou mettre à jour une maintenance curative existante.

## 📋 Fonctionnalités disponibles

### ✅ Modification des données de base
- **Localisation** : Changer l'équipement et sa localisation
- **Date d'intervention** : Modifier la date réelle de l'intervention
- **Description** : Corriger ou améliorer la description de la maintenance
- **Temps passé** : Ajuster le nombre d'heures
- **Nombre de personnes** : Modifier le nombre de personnes impliquées

### ✅ Gestion des pièces utilisées
- **Ajouter des pièces** : Inclure de nouvelles pièces utilisées
- **Supprimer des pièces** : Retirer des pièces de la liste
- **Modifier les quantités** : Ajuster les quantités de pièces
- **Gestion automatique du stock** : Les mouvements de stock sont automatiquement ajustés

## 🔧 Comment utiliser

### 1. Accéder à la modification
1. Aller sur la page **Maintenance Curative**
2. Trouver la maintenance à modifier dans le tableau
3. Cliquer sur le bouton **🖊️ Modifier** (icône crayon)

### 2. Modifier les informations
1. **Localisation** : Sélectionner une nouvelle localisation si nécessaire
2. **Équipement** : Choisir un nouvel équipement (se met à jour automatiquement selon la localisation)
3. **Date d'intervention** : Modifier la date si nécessaire
4. **Description** : Corriger ou améliorer la description
5. **Temps et personnes** : Ajuster selon les besoins

### 3. Gérer les pièces utilisées
1. **Pièces existantes** : Les pièces déjà utilisées sont pré-remplies
2. **Modifier les quantités** : Ajuster les quantités directement
3. **Supprimer des pièces** : Cliquer sur la poubelle 🗑️
4. **Ajouter des pièces** : Cliquer sur "Ajouter une pièce"
5. **Validation automatique** : Le système vérifie les stocks disponibles

### 4. Sauvegarder les modifications
1. Vérifier toutes les informations
2. Cliquer sur **"Modifier la maintenance curative"**
3. Confirmation : Message de succès s'affiche

## ⚠️ Points importants

### 🔄 Gestion automatique du stock
- **Annulation automatique** : Les anciennes sorties de stock sont annulées
- **Nouvelles sorties** : Les nouvelles pièces sont retirées du stock
- **Traçabilité** : Tous les mouvements sont enregistrés avec motif "Modification maintenance curative"

### 🛡️ Sécurité des données
- **Validation** : Toutes les données sont validées avant sauvegarde
- **Rollback** : En cas d'erreur, toutes les modifications sont annulées
- **Traçabilité** : Les modifications sont tracées dans les mouvements de stock

### 📊 Impact sur les rapports
- **Rapports mis à jour** : Les rapports envoyés après modification reflètent les nouvelles données
- **Historique préservé** : L'historique des mouvements de stock est conservé

## 🎨 Interface utilisateur

### Boutons d'action dans le tableau
- **👁️ Voir** : Afficher les détails (modal)
- **🖊️ Modifier** : Modifier la maintenance curative
- **📧 Envoyer** : Envoyer le rapport par email

### Formulaire de modification
- **Pré-remplissage** : Toutes les données actuelles sont pré-remplies
- **Validation en temps réel** : Vérification des stocks disponibles
- **Interface intuitive** : Même interface que l'ajout, mais avec données existantes

## 🔍 Cas d'usage typiques

### 1. Correction d'erreur de saisie
- **Problème** : Date d'intervention incorrecte
- **Solution** : Modifier la date et sauvegarder

### 2. Ajout de pièces oubliées
- **Problème** : Pièces utilisées non enregistrées
- **Solution** : Ajouter les pièces manquantes

### 3. Modification de la description
- **Problème** : Description incomplète ou imprécise
- **Solution** : Améliorer la description de la maintenance

### 4. Changement d'équipement
- **Problème** : Mauvais équipement sélectionné
- **Solution** : Changer l'équipement et la localisation

## 🚀 Avantages

### ✅ Flexibilité
- Modifications possibles à tout moment
- Pas de limitation de temps

### ✅ Intégrité des données
- Gestion automatique du stock
- Traçabilité complète

### ✅ Simplicité d'utilisation
- Interface familière
- Validation automatique

### ✅ Sécurité
- Rollback en cas d'erreur
- Validation des données

## 📝 Notes techniques

### Base de données
- **Table** : `maintenance_curative`
- **Relations** : `equipement`, `pieces_utilisees_curatives`
- **Mouvements** : `mouvement_piece` pour le stock

### Routes ajoutées
- **GET/POST** : `/maintenance-curative/modifier/<id>`
- **Template** : `modifier_maintenance_curative.html`

### Permissions
- **Accès** : Utilisateur avec permission `maintenance_curative`
- **Modification** : Même niveau d'accès que la consultation

---

## 🎉 Conclusion

La fonctionnalité de modification des maintenances curatives offre une flexibilité complète pour corriger et améliorer les données, tout en maintenant l'intégrité du système de gestion des stocks et la traçabilité des opérations. 