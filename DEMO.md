# Guide de Démonstration - Application de Maintenance Préventive

## 🚀 Démarrage rapide

L'application est maintenant lancée et accessible à l'adresse : **http://localhost:5000**

## 📋 Étapes de démonstration

### 1. Connexion
- Ouvrez votre navigateur et allez sur http://localhost:5000
- Cliquez sur "Se connecter" (mode démo - aucune authentification requise)

### 2. Configuration initiale (dans l'ordre)

#### A. Créer des sites
1. Cliquez sur "Sites" dans le menu de gauche
2. Cliquez sur "Ajouter un site"
3. Remplissez :
   - **Nom** : "Site Principal"
   - **Description** : "Site principal de production"
4. Cliquez sur "Enregistrer"

#### B. Créer des localisations
1. Cliquez sur "Localisations" dans le menu
2. Cliquez sur "Ajouter une localisation"
3. Remplissez :
   - **Nom** : "Atelier 1"
   - **Description** : "Atelier de production principal"
   - **Site** : Sélectionnez "Site Principal"
4. Cliquez sur "Enregistrer"

#### C. Créer des équipements
1. Cliquez sur "Équipements" dans le menu
2. Cliquez sur "Ajouter un équipement"
3. Remplissez :
   - **Nom** : "Machine CNC-001"
   - **Description** : "Machine à commande numérique"
   - **Localisation** : Sélectionnez "Atelier 1"
   - **Pièces de rechange** : Cochez les pièces que vous voulez associer
4. Cliquez sur "Enregistrer"

#### D. Gérer les pièces d'un équipement existant
1. Dans la liste des équipements, cliquez sur le bouton "📦" (icône boîtes)
2. Cochez/décochez les pièces que vous voulez associer à cet équipement
3. Cliquez sur "Enregistrer les associations"

#### E. Créer des lieux de stockage
1. Cliquez sur "Lieux de stockage" dans le menu
2. Cliquez sur "Ajouter un lieu de stockage"
3. Remplissez :
   - **Nom** : "Zone A"
   - **Description** : "Zone de stockage principale pour les pièces courantes"
4. Cliquez sur "Enregistrer"

#### F. Ajouter des pièces de rechange
1. Cliquez sur "Pièces de rechange" dans le menu
2. Cliquez sur "Ajouter une pièce"
3. Remplissez :
   - **Référence STE** : "STE-001"
   - **Item** : "Roulement à billes"
   - **Description** : "Roulement 6205-2RS"
   - **Lieu de stockage** : Sélectionnez "Zone A"
   - **Quantité en stock** : 10
   - **Stock minimum** : 2
   - **Stock maximum** : 20
4. Cliquez sur "Enregistrer"

### 3. Planification des maintenances

#### A. Créer une maintenance
1. Cliquez sur "Maintenances" dans le menu
2. Cliquez sur "Ajouter une maintenance"
3. Remplissez :
   - **Titre** : "Maintenance préventive CNC-001"
   - **Description** : "Vérification et lubrification hebdomadaire"
   - **Équipement** : Sélectionnez "Machine CNC-001"
   - **Périodicité** : "Semaine"
   - **Date de la première maintenance** : Date d'aujourd'hui
4. Cliquez sur "Enregistrer"

### 4. Utilisation du calendrier

#### A. Consulter le calendrier
1. Cliquez sur "Calendrier" dans le menu
2. Vous verrez les maintenances planifiées pour la semaine

#### B. Réaliser une maintenance
1. Dans le calendrier, cliquez sur "Réaliser" pour une maintenance
2. Ajoutez un commentaire : "Maintenance réalisée avec succès"
3. Si vous avez utilisé des pièces, sélectionnez-les dans la liste
   - Les pièces marquées "ASSOCIÉE" sont spécifiquement liées à cet équipement
4. Cliquez sur "Marquer comme réalisée"

### 5. Gestion des stocks

#### A. Réapprovisionner
1. Retournez sur "Pièces de rechange"
2. Cliquez sur le bouton "+" à côté d'une pièce
3. Entrez la quantité à ajouter
4. Cliquez sur "Ajouter au stock"

#### B. Consulter les mouvements
1. Cliquez sur "Mouvements" dans le menu
2. Vous verrez l'historique des entrées et sorties

## 🎯 Fonctionnalités clés à tester

### ✅ Gestion hiérarchique
- Sites → Localisations → Équipements
- Navigation fluide entre les niveaux

### ✅ Maintenance préventive
- Création de tâches avec périodicité
- Calendrier hebdomadaire
- Suivi des interventions

### ✅ Gestion des pièces
- Catalogue complet
- Gestion des stocks
- Réapprovisionnement
- Mouvements de stock
- Association des pièces aux équipements
- Lieux de stockage organisés

### ✅ Notifications
- Emails automatiques (si configuré)

## 🔧 Configuration email (optionnel)

Pour activer les emails automatiques :

1. Créez un fichier `.env` basé sur `env_example.txt`
2. Configurez vos paramètres Gmail :
   ```
   MAIL_USERNAME=votre-email@gmail.com
   MAIL_PASSWORD=votre-mot-de-passe-app
   ```
3. Redémarrez l'application

## 📊 Tableau de bord

Le tableau de bord affiche :
- Nombre de sites, équipements, maintenances, pièces
- Maintenances de la semaine
- Pièces en rupture de stock

## 🎨 Interface utilisateur

- **Design moderne** avec Bootstrap 5
- **Responsive** (mobile-friendly)
- **Navigation intuitive** avec sidebar
- **Modales** pour les actions rapides
- **Badges colorés** pour les statuts

## 🚀 Prochaines étapes

1. **Données réelles** : Remplacez les exemples par vos vraies données
2. **Authentification** : Implémentez une vraie authentification
3. **Base de données** : Migrez vers PostgreSQL pour la production
4. **Emails** : Configurez les notifications email
5. **Rapports** : Ajoutez des rapports et exports

---

**L'application est prête à être utilisée !** 🎉 