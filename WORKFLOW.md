# 🥦 Open Food Facts — Workflow de Prédiction du Nutri-Score
> Pipeline complet : de l'import des données brutes à la prédiction du Nutri-Score sur les produits inconnus.

---

## 📋 Vue d'ensemble

```
data_brut.csv (~12 Go)
        │
        ▼
┌────────────────────────────┐
│  ÉTAPE 1 · Extraction      │  traitement_donnees_polars.ipynb
│  (Polars, par batch)       │
└────────────┬───────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
produits_avec_     produits_sans_
nutriscore.csv     nutriscore.csv
(~106 000 lignes)  (~33 000 lignes)
     │                │
     └───────┬────────┘
             ▼
┌────────────────────────────┐
│  ÉTAPE 2 · Nettoyage       │  Nutri/prepa_données.ipynb
│  & Préparation             │
└────────────┬───────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
traité_avec_       traité_sans_
nutriscore.csv     nutriscore.csv
(~104 000 lignes)  (~32 000 lignes)
     │                │
     └───────┬────────┘
             ▼
┌────────────────────────────┐
│  ÉTAPE 3 · Modélisation    │  (3 notebooks, du plus simple au plus avancé)
└────────────┬───────────────┘
             │
     ┌───────┼────────────────┐
     ▼       ▼                ▼
  Notebook  Notebook       Notebook
  RF        Itératif       Optimisé
             │
             ▼
predictions_sans_nutriscore_XXX.csv
```

---

## 📂 Structure des fichiers

| Fichier / Dossier | Rôle |
|---|---|
| `data_brut.csv` | Source brute Open Food Facts (~12 Go, format TSV) |
| `traitement_donnees_polars.ipynb` | **Étape 1** : Extraction et filtrage par batch |
| `Nutri/produits_avec_nutriscore.csv` | Produits FR avec grade A–E (données d'entraînement) |
| `Nutri/produits_sans_nutriscore.csv` | Produits FR sans grade (cibles de prédiction) |
| `Nutri/prepa_données.ipynb` | **Étape 2** : Nettoyage, normalisation, export |
| `Nutri/traité_avec_nutriscore.csv` | Données d'entraînement nettoyées |
| `Nutri/traité_sans_nutriscore.csv` | Données de prédiction nettoyées |
| `Nutri/prediction_nutriscore_rf.ipynb` | **Modèle V1** : Random Forest + Cross-Validation |
| `Nutri/prediction_nutriscore_iterative.ipynb` | **Modèle V2** : Random Forest + IterativeImputer |
| `Nutri/prediction_nutriscore_optimise.ipynb` | **Modèle V3** : LightGBM + IterativeImputer (best) |
| `Nutri/predictions_nutriscore_rf.csv` | Prédictions du modèle V1 |
| `Nutri/predictions_sans_nutriscore_iterative.csv` | Prédictions du modèle V2 |
| `Nutri/predictions_sans_nutriscore_optimise.csv` | Prédictions du modèle V3 |

---

## 🔵 ÉTAPE 1 — Extraction des données brutes

**Notebook :** [`traitement_donnees_polars.ipynb`](traitement_donnees_polars.ipynb)

### 🎯 Objectif
Le fichier `data_brut.csv` pèse environ **12 Go** et contient des millions de produits alimentaires du monde entier. L'objectif est d'en extraire uniquement les produits **français** pertinents, en deux groupes distincts.

### ⚙️ Technologie : Polars en mode batch
Pour éviter de saturer la RAM, le fichier est lu par **échantillons de 100 000 lignes** (`BATCH_SIZE = 100_000`) grâce à la bibliothèque **Polars**, bien plus rapide que Pandas pour les gros volumes.

### 🔩 Pipeline 1 — Produits SANS Nutri-Score *(cibles de prédiction)*

**Critères de sélection :**
- ✅ Vendu en **France** (`countries_en` contient `france`)
- ✅ `nutriscore_score` est **null** (pas encore noté)
- ✅ Au moins **15 colonnes non nulles** (produit suffisamment documenté)

**Résultat :** `produits_sans_nutriscore.csv` — **33 216 produits × 130 colonnes**

### 🔩 Pipeline 2 — Produits AVEC Nutri-Score *(données d'entraînement)*

**Critères de sélection :**
- ✅ Vendu en **France**
- ✅ `nutriscore_grade` est une **lettre valide** (a / b / c / d / e) — exclusion de `"unknown"`, `"not-applicable"`, etc.
- ✅ Les **7 features nutritionnelles** du modèle sont toutes présentes (pas de null)

**Features requises :**
| Feature | Description |
|---|---|
| `energy_100g` | Énergie (kJ) pour 100g |
| `sugars_100g` | Sucres pour 100g |
| `saturated-fat_100g` | Graisses saturées pour 100g |
| `salt_100g` | Sel pour 100g |
| `fiber_100g` | Fibres pour 100g |
| `proteins_100g` | Protéines pour 100g |
| `fruits-vegetables-legumes_100g` | % fruits/légumes pour 100g |

**Résultat :** `produits_avec_nutriscore.csv` — **106 067 produits × 129 colonnes**

Distribution des grades :
```
d → 25 544  e → 25 228  c → 25 344  a → 18 018  b → 11 933
```

---

## 🟡 ÉTAPE 2 — Préparation & Nettoyage des données

**Notebook :** [`Nutri/prepa_données.ipynb`](Nutri/prepa_données.ipynb)

### 🎯 Objectif
Transformer les CSV bruts extraits à l'étape précédente en jeux de données propres et cohérents, prêts pour l'entraînement ML.

### ⚙️ Traitement appliqué

La fonction `preparer_donnees()` applique les traitements suivants sur les deux datasets :

| # | Transformation | Détail |
|---|---|---|
| 1 | **Sélection des colonnes** | 15 colonnes utiles uniquement (`code`, `product_name`, `nova_group`, nutriments, `nutriscore_grade`) |
| 2 | **Typage numérique** | Conversion forcée des colonnes numériques (`nova_group`, `additives_n`, nutriments) avec `pd.to_numeric(errors='coerce')` |
| 3 | **Suppression des produits sans nom** | `dropna(subset=['product_name'])` |
| 4 | **Plafonnement à 100g** | Valeurs > 100 → 100 ; valeurs < 0 → 0 |
| 5 | **Cohérence Sucres/Glucides** | Si `sugars > carbohydrates`, on remplace `sugars` par `carbohydrates` |
| 6 | **Élimination des aberrations** | Lignes où la somme (glucides + graisses + protéines + sel) > 100g sont supprimées |

**Résultats après nettoyage :**
- `traité_avec_nutriscore.csv` → **~104 313 lignes × 15 colonnes** (données d'entraînement)
- `traité_sans_nutriscore.csv` → **~32 394 lignes × 15 colonnes** (à prédire)

> **Note :** Un encodeur TF-IDF sur les noms de produits (`product_name`) est également prototypé dans ce notebook mais n'est pas utilisé dans les modèles finaux de prédiction du grade.

---

## 🟢 ÉTAPE 3 — Modélisation & Prédiction

Trois notebooks de modélisation ont été développés, par ordre croissant de sophistication.

---

### 🤖 Modèle V1 — Random Forest + Cross-Validation

**Notebook :** [`Nutri/prediction_nutriscore_rf.ipynb`](Nutri/prediction_nutriscore_rf.ipynb)  
**Sortie :** `predictions_nutriscore_rf.csv`

#### 🎯 But
Servir de **baseline solide** : un Random Forest classique avec imputation par médiane et validation croisée stratifiée.

#### ⚙️ Pipeline sklearn

```
SimpleImputer (médiane)
        │
        ▼
RandomForestClassifier
  ├── n_estimators = 200
  ├── min_samples_leaf = 5
  ├── class_weight = 'balanced'
  └── random_state = 42
```

#### 📊 Évaluation
- **Cross-Validation Stratifiée 5-Fold** (StratifiedKFold) sur 80% des données
- Holdout final 20% pour la matrice de confusion

| Métrique | Valeur |
|---|---|
| Val Accuracy (moyenne CV) | **~90.72%** |
| Val F1-macro (moyenne CV) | **~89.71%** |

#### 🔍 Pourquoi ce modèle ?
- **Random Forest** : ensemble d'arbres de décision, robuste aux outliers et faible risque d'overfitting
- **Imputation médiane** : simple et efficace pour les valeurs manquantes des nutriments
- **class_weight='balanced'** : compense le déséquilibre entre les grades (le grade B est moins représenté)

---

### 🤖 Modèle V2 — Random Forest + IterativeImputer

**Notebook :** [`Nutri/prediction_nutriscore_iterative.ipynb`](Nutri/prediction_nutriscore_iterative.ipynb)  
**Sortie :** `predictions_sans_nutriscore_iterative.csv`

#### 🎯 But
Améliorer la qualité de l'imputation en remplaçant la médiane par une **imputation itérative** basée sur les autres features.

#### ⚙️ Pipeline sklearn

```
IterativeImputer
  └── estimator = ExtraTreesRegressor (ou BayesianRidge)
        │
        ▼
RandomForestClassifier
```

#### 🔍 Pourquoi ce modèle ?
- **IterativeImputer** : impute chaque feature manquante en entraînant un modèle sur les autres features disponibles, itérativement. Beaucoup plus précis que la médiane lorsque les nutriments sont corrélés entre eux (ex : sucres ↔ glucides, graisses saturées ↔ graisses totales).
- **ExtraTreesRegressor** comme estimateur : rapide et adapté aux données numériques avec beaucoup de features

---

### 🤖 Modèle V3 — LightGBM + IterativeImputer *(version optimisée)*

**Notebook :** [`Nutri/prediction_nutriscore_optimise.ipynb`](Nutri/prediction_nutriscore_optimise.ipynb)  
**Sortie :** `predictions_sans_nutriscore_optimise.csv`

#### 🎯 But
Maximiser les performances en combinant la meilleure imputation (IterativeImputer) avec un classifieur gradient boosting puissant (LightGBM) et de nouvelles features engineerées.

#### ⚙️ Pipeline sklearn

```
IterativeImputer
  └── estimator = ExtraTreesRegressor(n_estimators=50)
        │
        ▼
LGBMClassifier
  ├── n_estimators = 300
  ├── learning_rate = 0.05
  ├── max_depth = 7
  ├── num_leaves = 63
  └── class_weight = 'balanced'
```

#### 🚀 Améliorations vs V1/V2

| # | Levier | Détail |
|---|---|---|
| 1 | **Features étendues** | + `nova_group`, `additives_n`, `sugars_ratio`, `sat_fat_ratio` |
| 2 | **IterativeImputer (ExtraTrees)** | Imputation itérative robuste |
| 3 | **LightGBM** | Gradient boosting rapide et précis (fallback : GradientBoostingClassifier) |
| 4 | **Class weight** | Équilibrage automatique des grades |
| 5 | **RandomizedSearchCV** | Optimisation des hyperparamètres (15 itérations, k=3) |
| 6 | **Scoring complet** | Rapport par grade, F1, matrices de confusion normalisée |

#### 🔧 Feature Engineering
```python
# Ratios dérivés (corrélés au grade)
sugars_ratio  = sugars_100g     / (carbohydrates_100g + 1e-6)
sat_fat_ratio = sat_fat_100g    / (fat_100g           + 1e-6)
```

#### 🔍 Pourquoi LightGBM ?
- **LightGBM** est un framework de Gradient Boosting optimisé pour la vitesse et la précision sur les données tabulaires
- Utilise le **leaf-wise tree growth** (vs level-wise pour XGBoost), plus efficace
- Gère nativement les **données éparses** et les **valeurs manquantes**
- Nettement plus performant que Random Forest sur les données nutritionnelles

---

## 🔬 Glossaire des concepts ML

| Terme | Définition |
|---|---|
| **Cross-Validation Stratifiée** | Division du dataset en k folds en conservant la proportion de chaque classe dans chaque fold |
| **SimpleImputer (médiane)** | Remplace les valeurs manquantes par la médiane de la colonne |
| **IterativeImputer** | Impute les valeurs manquantes en entraînant un modèle régresseur sur les autres features, plusieurs fois de suite |
| **Random Forest** | Ensemble de N arbres de décision ; chaque arbre est entraîné sur un sous-échantillon aléatoire |
| **LightGBM** | Gradient Boosting : construction séquentielle d'arbres, chaque arbre corrigeant les erreurs du précédent |
| **class_weight='balanced'** | Pondère automatiquement les classes pour compenser les déséquilibres (grade B rare → plus de poids) |
| **F1-macro** | Moyenne des F1-scores par classe (bon indicateur quand les classes sont déséquilibrées) |
| **RandomizedSearchCV** | Recherche aléatoire des meilleurs hyperparamètres (plus rapide que GridSearch) |
| **Hold-out** | Portion de données (20%) mise de côté et jamais vue pendant l'entraînement, pour l'évaluation finale |
| **OOB Error** | Out-Of-Bag : équivalent d'une validation interne pour Random Forest sans CV explicite |

---

## 🏆 Résumé des performances

| Modèle | Imputation | Classifieur | Val Accuracy | Val F1-macro |
|---|---|---|---|---|
| **V1 — RF baseline** | Médiane | RandomForest | ~90.7% | ~89.7% |
| **V2 — RF + Iterative** | IterativeImputer | RandomForest | +++ | +++ |
| **V3 — Optimisé** | IterativeImputer | LightGBM + HPO | 🏆 best | 🏆 best |

---

*Projet Open Food Facts — Prédiction du Nutri-Score*
