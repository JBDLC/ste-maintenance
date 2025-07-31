# Guide d'utilisation - Maintenance Curative

## 🛠️ Vue d'ensemble

La fonctionnalité de **Maintenance Curative** permet d'enregistrer les maintenances non prévues (curatives) qui ne sont pas liées au calendrier de maintenance préventive.

## 📋 Fonctionnalités

### ✅ Fonctionnalités implémentées

- **Page principale** : Liste de toutes les maintenances curatives avec possibilité de voir les détails
- **Ajout de maintenance curative** : Formulaire complet avec tous les champs demandés
- **Gestion des pièces** : Utilisation du stock existant avec mise à jour automatique
- **Envoi de rapports** : Génération et envoi de rapports PDF par email
- **Intégration complète** : Fonctionne avec le système de permissions existant

### 🎯 Champs du formulaire

1. **Localisation** (liste déroulante) - *Obligatoire*
2. **Équipement** (liste déroulante) - *Obligatoire*
3. **Description de l'équipement** (remplissage automatique)
4. **Maintenance réalisée** (zone de texte) - *Obligatoire*
5. **Temps passé** (en heures) - *Obligatoire*
6. **Nombre de personnes** - *Obligatoire*
7. **Pièces de rechange utilisées** (optionnel)

## 🚀 Comment utiliser

### 1. Accéder à la page

1. Connectez-vous à l'application
2. Dans le menu latéral, cliquez sur **"Maintenance Curative"** (icône 🔧)
3. Vous verrez la liste des maintenances curatives existantes

### 2. Ajouter une maintenance curative

1. Cliquez sur le bouton **"Ajouter une maintenance curative"**
2. Remplissez le formulaire :
   - **Localisation** : Sélectionnez la localisation
   - **Équipement** : Sélectionnez l'équipement (se remplit automatiquement selon la localisation)
   - **Description équipement** : Se remplit automatiquement
   - **Maintenance réalisée** : Décrivez la maintenance effectuée
   - **Temps passé** : Entrez le nombre d'heures (ex: 2.5)
   - **Nombre de personnes** : Entrez le nombre de personnes impliquées
   - **Pièces utilisées** : Optionnel, ajoutez les pièces consommées

3. Cliquez sur **"Enregistrer la maintenance curative"**

### 3. Gestion des pièces

- **Ajouter une pièce** : Cliquez sur "Ajouter une pièce"
- **Sélectionner** : Choisissez la pièce dans la liste (le stock disponible est affiché)
- **Quantité** : Entrez la quantité utilisée (ne peut pas dépasser le stock disponible)
- **Supprimer** : Cliquez sur l'icône 🗑️ pour supprimer une ligne

### 4. Consulter les détails

- Cliquez sur l'icône 👁️ pour voir les détails complets
- Une fenêtre modale s'ouvre avec toutes les informations

### 5. Envoyer un rapport

- Cliquez sur l'icône 📧 pour envoyer le rapport par email
- Le rapport PDF est généré automatiquement
- L'email est envoyé à l'adresse configurée dans les paramètres

## 📊 Intégration avec le système existant

### ✅ Compatibilité

- **Stock de pièces** : Utilise le même système de gestion des pièces
- **Mouvements** : Les sorties sont automatiquement enregistrées dans la page "Magasin"
- **Permissions** : Respecte le système de permissions existant
- **Email** : Utilise la même configuration SMTP que les autres rapports

### 🔄 Flux de données

1. **Sélection d'équipement** → Récupération automatique de la description
2. **Utilisation de pièces** → Mise à jour automatique du stock
3. **Enregistrement** → Création d'un mouvement de sortie
4. **Rapport** → Génération PDF et envoi email

## 🎨 Interface utilisateur

### Page principale
- **Tableau responsive** avec toutes les maintenances
- **Actions** : Voir détails et envoyer rapport
- **État vide** : Message d'encouragement si aucune maintenance

### Formulaire d'ajout
- **Interface intuitive** avec validation en temps réel
- **Sélection dynamique** des équipements selon la localisation
- **Gestion flexible** des pièces (ajout/suppression dynamique)
- **Validation** des quantités selon le stock disponible

## 🔧 Configuration technique

### Tables de base de données

```sql
-- Table principale
maintenance_curative
- id (PK)
- equipement_id (FK)
- description_maintenance
- temps_passe (heures)
- nombre_personnes
- date_realisation

-- Table des pièces utilisées
piece_utilisee_curative
- id (PK)
- maintenance_curative_id (FK)
- piece_id (FK)
- quantite
```

### Permissions

La page nécessite la permission `maintenance_curative` qui est automatiquement ajoutée lors de la création d'un nouvel utilisateur.

## 🚨 Points d'attention

### Validation des données
- **Temps passé** : Doit être positif
- **Nombre de personnes** : Doit être au moins 1
- **Quantité de pièces** : Ne peut pas dépasser le stock disponible
- **Équipement** : Doit être sélectionné après la localisation

### Gestion des erreurs
- **Stock insuffisant** : Empêche l'utilisation de pièces
- **Configuration email** : Vérifie la configuration SMTP avant envoi
- **Données manquantes** : Validation côté client et serveur

## 📈 Avantages

1. **Traçabilité complète** : Toutes les maintenances curatives sont enregistrées
2. **Intégration parfaite** : Utilise l'infrastructure existante
3. **Rapports automatisés** : Génération et envoi automatiques
4. **Gestion du stock** : Mise à jour automatique des stocks
5. **Interface intuitive** : Facile à utiliser pour tous les utilisateurs

## 🔮 Évolutions futures possibles

- **Historique détaillé** : Filtres par date, équipement, localisation
- **Statistiques** : Temps moyen, coûts, fréquence
- **Notifications** : Alertes pour maintenances fréquentes
- **Export** : Export Excel des données
- **Photos** : Ajout de photos des interventions 