# Guide : Données Fournisseur pour les Pièces de Rechange

## 🆕 Nouvelle fonctionnalité ajoutée

### **Champ "Données fournisseur"**
- **Type** : Champ texte facultatif
- **Emplacement** : Formulaire d'ajout/modification de pièces
- **Stockage** : Base de données (colonne `donnees_fournisseur`)

## 📍 **Où trouver ce champ**

### 1. **Ajout d'une nouvelle pièce**
- Aller dans **Pièces de rechange** → **Ajouter**
- Le champ apparaît après la **Description**
- Placeholder : "Informations sur le fournisseur, contact, références..."

### 2. **Modification d'une pièce existante**
- Dans la liste des pièces, cliquer sur le bouton **Modifier** (icône crayon)
- Le champ est pré-rempli avec les données existantes

### 3. **Affichage dans la liste**
- Nouvelle colonne **"Fournisseur"** dans le tableau des pièces
- Visible uniquement sur les écrans larges (XL)
- Affiche une icône d'information si des données sont présentes

## 💡 **Exemples d'utilisation**

### **Informations de contact**
```
Nom : ABC Fournitures
Téléphone : 01 23 45 67 89
Email : contact@abc-fournitures.fr
```

### **Références fournisseur**
```
Réf. fournisseur : ABC-12345
Code client : CLIENT-001
Site web : www.abc-fournitures.fr
```

### **Conditions commerciales**
```
Délai de livraison : 48h
Conditions de paiement : 30 jours
Remise : 5% à partir de 1000€
```

## 🔧 **Migration effectuée**

- ✅ **Modèle de données** : Colonne `donnees_fournisseur` ajoutée
- ✅ **Formulaire d'ajout** : Champ intégré
- ✅ **Formulaire de modification** : Champ intégré
- ✅ **Affichage liste** : Colonne ajoutée
- ✅ **Base de données** : Migration automatique

## 📱 **Responsive design**

- **Écrans larges (XL)** : Colonne "Fournisseur" visible
- **Écrans moyens (LG)** : Colonne masquée pour économiser l'espace
- **Mobile** : Optimisé pour les petits écrans

## 🎯 **Avantages**

1. **Traçabilité** : Garder les informations des fournisseurs
2. **Maintenance** : Faciliter la commande de pièces
3. **Gestion** : Centraliser les contacts fournisseurs
4. **Flexibilité** : Champ libre pour tous types d'informations

## 🚀 **Comment utiliser**

1. **Ajouter une pièce** → Remplir le champ "Données fournisseur"
2. **Modifier une pièce** → Mettre à jour les informations
3. **Consulter** → Voir l'icône dans la liste des pièces
4. **Survoler** → Afficher le contenu complet au survol

---

*Cette fonctionnalité est entièrement facultative et n'affecte pas le fonctionnement existant de l'application.* 