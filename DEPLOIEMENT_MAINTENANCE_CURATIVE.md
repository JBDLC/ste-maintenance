# Guide de déploiement - Maintenance Curative

## 🚀 Déploiement en production

### 1. Prérequis

- Base de données PostgreSQL configurée
- Variables d'environnement configurées
- Application déployée sur Render/Heroku/etc.

### 2. Étapes de déploiement

#### A. Mise à jour du code

1. **Pousser les modifications** sur votre repository Git
```bash
git add .
git commit -m "Ajout fonctionnalité maintenance curative"
git push origin main
```

2. **Redéployer l'application** (automatique sur Render/Heroku)

#### B. Migration de la base de données

1. **Se connecter à votre serveur de production** ou utiliser la console Render

2. **Exécuter la migration PostgreSQL** :
```bash
python migrate_postgresql.py
```

3. **Vérifier que la migration s'est bien passée** :
- La colonne `date_intervention` doit être ajoutée
- Les enregistrements existants doivent être mis à jour

#### C. Vérification

1. **Accéder à l'application** en production
2. **Se connecter** avec l'utilisateur admin
3. **Vérifier** que "Maintenance Curative" apparaît dans le menu
4. **Tester** l'ajout d'une maintenance curative

### 3. Fonctionnalités ajoutées

#### ✅ Nouveaux champs

- **Date d'intervention** : Date réelle de l'intervention (affichée dans le tableau)
- **Date de saisie** : Date de création de l'enregistrement (pour traçabilité)

#### ✅ Interface utilisateur

- **Page principale** : Liste des maintenances curatives avec date d'intervention
- **Formulaire d'ajout** : Champ date d'intervention obligatoire
- **Modal de détails** : Affichage des deux dates (intervention + saisie)
- **Rapports PDF** : Incluent la date d'intervention

#### ✅ Intégration

- **Stock de pièces** : Mise à jour automatique lors de l'utilisation
- **Mouvements** : Enregistrement des sorties dans la page Magasin
- **Permissions** : Respect du système existant
- **Email** : Envoi de rapports avec date d'intervention

### 4. Structure de la base de données

#### Tables ajoutées

```sql
-- Table principale
maintenance_curative
- id (PK)
- equipement_id (FK)
- description_maintenance (TEXT)
- temps_passe (FLOAT)
- nombre_personnes (INTEGER)
- date_intervention (DATE) ← NOUVEAU
- date_realisation (TIMESTAMP)

-- Table des pièces utilisées
piece_utilisee_curative
- id (PK)
- maintenance_curative_id (FK)
- piece_id (FK)
- quantite (INTEGER)
```

#### Permissions

- `maintenance_curative` : Permission pour accéder à la fonctionnalité

### 5. Utilisation

#### A. Accès
1. Menu latéral → "Maintenance Curative" (icône 🔧)
2. Bouton "Ajouter une maintenance curative"

#### B. Formulaire
1. **Localisation** (liste déroulante)
2. **Équipement** (se remplit selon la localisation)
3. **Description équipement** (remplissage automatique)
4. **Date d'intervention** ← **NOUVEAU**
5. **Maintenance réalisée** (description)
6. **Temps passé** (en heures)
7. **Nombre de personnes**
8. **Pièces utilisées** (optionnel)

#### C. Actions
- **Voir détails** : Modal avec toutes les informations
- **Envoyer rapport** : PDF par email avec date d'intervention

### 6. Dépannage

#### Problème : La page n'apparaît pas
- Vérifier que la permission `maintenance_curative` est activée pour l'utilisateur
- Se déconnecter/reconnecter

#### Problème : Erreur de migration
- Vérifier que PostgreSQL est bien configuré
- Vérifier les permissions de la base de données
- Exécuter manuellement les requêtes SQL si nécessaire

#### Problème : Champ date manquant
- Vérifier que la migration s'est bien exécutée
- Redémarrer l'application

### 7. Tests recommandés

1. **Ajouter** une maintenance curative complète
2. **Vérifier** que la date d'intervention s'affiche correctement
3. **Tester** l'utilisation de pièces (mise à jour du stock)
4. **Envoyer** un rapport par email
5. **Vérifier** les mouvements dans la page Magasin

### 8. Notes importantes

- **Date d'intervention** : Obligatoire, affichée dans le tableau principal
- **Date de saisie** : Automatique, pour traçabilité
- **Stock** : Mise à jour automatique lors de l'utilisation de pièces
- **Permissions** : Respect du système existant

La fonctionnalité est maintenant prête pour la production ! 🎉 