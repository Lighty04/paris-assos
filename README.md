# Paris Subventions - Site de suivi des contributions municipales

## Description

Ce site permet de suivre de manière transparente les subventions accordées par la Ville de Paris aux associations. Les données affichées sont des **subventions nettes** calculées pour éviter le double-comptage et refléter les véritables contributions des contribuables.

## Méthodologie de calcul des subventions nettes

### Objectif

Calculer les **véritables contributions des contribuables parisiens** en reconciliant les acomptes, soldes, remboursements et ajustements.

### Logique de calcul

```
net_subvention = 0

Pour chaque année:
  - Subventions normales → AJOUTER au net
  - Acomptes → AJOUTER au net (paiement partiel)
  - Soldes → AJOUTER au net (complète l'engagement)
  - Régularisations → AJOUTER au net (ajustements de fin d'exercice)
  - Remboursements → SOUSTRAIRE du net (retours de fonds)
  - Remboursements d'emprunt → EXCLURE (non subvention)

Cas spécial:
  - Si une année a à la fois un acompte ET un solde:
    → Total = acompte + solde (parties d'un même engagement)
    → Pas de double-comptage car ce sont des paiements séparés
```

### Types détectés automatiquement

Le système analyse le texte de chaque subvention pour classifier :

| Type | Motifs détectés | Traitement |
|------|-----------------|------------|
| **Acompte** | "acompte", "a compte" | Additionné au net |
| **Solde** | "solde" (hors "soldat") | Additionné au net |
| **Subvention** | "subvention" | Additionné au net |
| **Régularisation** | "régularisation", "regularisation" | Additionné au net |
| **Remboursement** | "remboursement", "rembours" | Soustrait du net |
| **Emprunt** | "emprunt" + "remboursement" | Exclu du calcul |

### Indicateurs de qualité des données

- **Données nettes** : Pourcentage d'années sans alerte
- **Données suspicieuses** : Années avec alertes (acompte sans solde, montant négatif, doublons potentiels)

### Exemple de transformation

**Philharmonie de Paris (2015)** :
- Fonctionnement : 6,000,000 €
- Remboursement emprunt : 7,599,654 € ❌ exclu
- Remboursement emprunt : 8,058,579 € ❌ exclu
- **Net 2015** : 6,000,000 € (au lieu de 21,658,233 € brut)

## Structure des données

### data_net.json

Fichier principal contenant les associations avec subventions nettes calculées :

```json
{
  "stats": {
    "totalAssociations": 13033,
    "totalNetAmount": 3529741747,
    "totalRawAmount": 3545520686,
    "difference": 15778939,
    "reductionPercent": 0.4,
    "dataQuality": {
      "totalYears": 43486,
      "cleanYears": 41444,
      "suspiciousYears": 2042,
      "cleanPercent": 95.3
    }
  },
  "associations": [
    {
      "name": "...",
      "siret": "...",
      "netTotalAmount": 26665000,
      "netSubventions": [
        {
          "year": "2015",
          "net_amount": 6000000,
          "raw_amount": 21658233,
          "flags": [],
          "components": { ... }
        }
      ],
      "netYearlyData": { "2015": 6000000, ... }
    }
  ]
}
```

### Champs ajoutés par le calcul net

- `netTotalAmount` : Montant total net de l'association
- `netSubventions` : Liste des subventions par année avec montants nets
  - `net_amount` : Montant net calculé
  - `raw_amount` : Montant brut original
  - `flags` : Alertes de qualité (incomplete_acompte_no_solde, negative_net, etc.)
  - `components` : Détail des composants (acompte, solde, subvention, etc.)
- `netYearlyData` : Dictionnaire année → montant net

## API Endpoints

### `/api/associations`
Liste paginée des associations avec données nettes.

**Paramètres** :
- `page` : Numéro de page (défaut: 1)
- `per_page` : Nombre par page (défaut: 100)
- `search` : Recherche texte
- `year` : Filtrer par année
- `sector` : Filtrer par secteur
- `sort` : Tri (total_desc, total_asc, lastYear_desc, etc.)

### `/api/associations/{siret}`
Détails d'une association avec subventions nettes.

### `/api/associations/raw/{siret}`
Données brutes non ajustées (pour transparence).

### `/api/associations/raw`
Liste complète des données brutes.

### `/api/stats`
Statistiques globales (montants nets).

### `/api/stats/quality`
Métriques de qualité des données.

### `/api/filters`
Liste des années et secteurs disponibles.

## Déploiement

### Prérequis

- Python 3.x
- Fichier `data_net.json` généré

### Lancement

```bash
cd /home/decisionhelper/website
python3 server.py
```

Le serveur écoute sur le port 8010.

### Génération des données nettes

```bash
python3 calculate_net_subventions.py
```

Ce script :
1. Charge `data.json` (données brutes)
2. Applique la logique de calcul net
3. Génère `data_net.json`
4. Affiche les statistiques de vérification

## Résultats actuels

- **Associations** : 13,033
- **Montant net total** : 3,529,741,747 €
- **Montant brut total** : 3,545,520,686 €
- **Différence** : 15,778,939 € (réduction de 0.4%)
- **Qualité des données** : 95.3% d'années "propres"

### Exemples de corrections significatives

| Association | Montant brut | Montant net | Réduction |
|-------------|--------------|-------------|-----------|
| Philharmonie de Paris | 42,323,233 € | 26,665,000 € | 37% |

## Licence

Données publiques - Ville de Paris
