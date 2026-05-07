# 🌍 Open Food Facts — Workflow de Prédiction de l'Éco-Score
> Pipeline complet : de l'import des données brutes à la prédiction de l'Éco-Score sur les produits inconnus, avec approche textuelle (NLP).

---

## 📋 Vue d'ensemble

```
data_brut.csv (~12 Go)
        │
        ▼
┌────────────────────────────┐
│  ÉTAPE 1 · Extraction      │  eco/traitement_donnees_ecoscore_polars.ipynb
│  (Polars, par batch)       │
└────────────┬───────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
produits_avec_     produits_sans_
ecoscore.csv       ecoscore.csv
     │                │
     └───────┬────────┘
             ▼
┌────────────────────────────┐
│  ÉTAPE 2 · Nettoyage       │  eco/prepa_donnees_ecoscore.ipynb
│  & Préparation             │
└────────────┬───────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
traite_avec_       traite_sans_
ecoscore.csv       ecoscore.csv
     │                │
     └───────┬────────┘
             ▼
┌────────────────────────────┐
│  ÉTAPE 3 · Modélisation    │  eco/prediction_ecoscore_rf.ipynb
└────────────┬───────────────┘
             │
             ▼
produits_predictions_ecoscore.csv
```

---

## 📂 Structure des fichiers

| Fichier / Dossier | Rôle |
|---|---|
| `data_brut.csv` | Source brute Open Food Facts (~12 Go, format TSV) |
| `eco/traitement_donnees_ecoscore_polars.ipynb` | **Étape 1** : Extraction et filtrage par batch (Polars) |
| `eco/produits_avec_ecoscore.csv` | Produits FR avec grade a–e (données d'entraînement) |
| `eco/produits_sans_ecoscore.csv` | Produits FR sans grade (cibles de prédiction) |
| `eco/prepa_donnees_ecoscore.ipynb` | **Étape 2** : Nettoyage textuel (NLP), normalisation, export |
| `eco/traite_avec_ecoscore.csv` | Données d'entraînement nettoyées |
| `eco/traite_sans_ecoscore.csv` | Données de prédiction nettoyées |
| `eco/prediction_ecoscore_rf.ipynb` | **Modèle** : Random Forest + NLP (TF-IDF) |
| `eco/produits_predictions_ecoscore.csv` | Prédictions du modèle sur les produits sans Éco-Score |

---

## 🔵 ÉTAPE 1 — Extraction des données brutes

**Notebook :** [`eco/traitement_donnees_ecoscore_polars.ipynb`](eco/traitement_donnees_ecoscore_polars.ipynb)

### 🎯 Objectif
Le fichier `data_brut.csv` pèse environ **12 Go** et contient des millions de produits. L'objectif est d'en extraire uniquement les produits **français** pertinents pour l'Éco-Score, en les séparant en données avec et sans score.

### ⚙️ Technologie : Polars en mode batch
Pour éviter de saturer la RAM, le fichier est lu par **échantillons de 100 000 lignes** (`BATCH_SIZE = 100_000`) grâce à la bibliothèque **Polars**.

### 🔩 Pipeline 1 — Produits SANS Éco-Score *(cibles de prédiction)*

**Critères de sélection :**
- ✅ Vendu en **France** (`countries_en` contient `france`)
- ✅ `environmental_score_score` est **null** (pas encore noté)
- ✅ Au moins **15 colonnes non nulles** (produit suffisamment documenté)

**Résultat :** `produits_sans_ecoscore.csv`

### 🔩 Pipeline 2 — Produits AVEC Éco-Score *(données d'entraînement)*

**Critères de sélection :**
- ✅ Vendu en **France**
- ✅ `environmental_score_grade` est une **lettre valide** (a / b / c / d / e)
- ✅ Les colonnes **`categories`** et **`ingredients_text`** ne sont pas nulles.

**Features requises :**
L'Éco-Score repose beaucoup sur l'origine et les ingrédients.
- Features Textuelles : `categories`, `labels`, `packaging`, `origins`, `ingredients_text`, `ingredients_analysis_tags`
- Features Nutritionnelles : Énergie, Sucres, Graisses saturées, Sel, Fibres, Protéines, Fruits/Légumes.

**Équilibrage :**
Ce pipeline intègre un processus d'équilibrage des classes (grades `a` à `e`) pour garantir que le modèle d'entraînement s'entraîne sur un nombre homogène de produits par grade (`TARGET_PAR_GRADE`).

**Résultat :** `produits_avec_ecoscore.csv`

---

## 🟡 ÉTAPE 2 — Préparation & Nettoyage des données

**Notebook :** [`eco/prepa_donnees_ecoscore.ipynb`](eco/prepa_donnees_ecoscore.ipynb)

### 🎯 Objectif
Nettoyer le texte (ingrédients, catégories) et formater les colonnes nutritionnelles pour préparer le jeu de données au modèle NLP + Machine Learning.

### ⚙️ Traitement appliqué

| # | Transformation | Détail |
|---|---|---|
| 1 | **Filtrage des noms** | Suppression des produits n'ayant pas de `product_name`. |
| 2 | **Nettoyage textuel (NLP)** | Remplacement des NaN par des chaînes vides, conversion en minuscules, suppression des sauts de ligne sur les colonnes textuelles (catégories, labels, packaging, etc.). |
| 3 | **Typage numérique** | Conversion forcée des colonnes nutritionnelles en valeurs numériques avec `pd.to_numeric(errors='coerce')`. |
| 4 | **Filtrage cible (Train)** | On ne conserve que les lignes dont `environmental_score_grade` est valide (a, b, c, d, e). |

**Résultats après nettoyage :**
- `traite_avec_ecoscore.csv` (données d'entraînement)
- `traite_sans_ecoscore.csv` (à prédire)

---

## 🟢 ÉTAPE 3 — Modélisation & Prédiction

**Notebook :** [`eco/prediction_ecoscore_rf.ipynb`](eco/prediction_ecoscore_rf.ipynb)

### 🎯 But
L'Éco-Score dépend majoritairement des ingrédients et des catégories. L'objectif est d'utiliser un modèle Random Forest classique couplé à une vectorisation TF-IDF du texte (NLP) pour prédire les scores.

### ⚙️ Pipeline sklearn

```
ColumnTransformer
  ├── TF-IDF (max_features=100) sur 'categories'
  ├── TF-IDF (max_features=200) sur 'ingredients_text'
  └── SimpleImputer (médiane) sur les features numériques
        │
        ▼
RandomForestClassifier
  ├── n_estimators = 100
  ├── min_samples_leaf = 5
  ├── class_weight = 'balanced'
  └── random_state = 42
```

### 🚀 Points clés du modèle

| # | Levier | Détail |
|---|---|---|
| 1 | **NLP (TF-IDF)** | Les champs texte (catégories et ingrédients) sont découpés en mots-clés pondérés (TF-IDF). |
| 2 | **ColumnTransformer** | Combine habilement le traitement textuel et numérique en une seule matrice. |
| 3 | **Random Forest** | Ensemble d'arbres de décision, robuste pour classer à partir de features éparses générées par le TF-IDF. |

**Sortie :** `produits_predictions_ecoscore.csv` contient les nouveaux produits de la base Open Food Facts avec la colonne `environmental_score_grade_predicted`.

---

## 🔬 Glossaire des concepts ML spécifiques

| Terme | Définition |
|---|---|
| **TF-IDF (TfidfVectorizer)** | Mesure statistique (Term Frequency-Inverse Document Frequency) qui évalue l'importance d'un mot dans un document par rapport à une collection. |
| **ColumnTransformer** | Outil Scikit-Learn permettant d'appliquer différentes transformations (ex: TF-IDF pour le texte, imputation pour les nombres) à différentes colonnes simultanément. |
| **Pipeline** | Enchaînement séquentiel d'étapes de traitement (ex: Preprocessing > Modèle) pour éviter la fuite de données et simplifier l'exécution. |
| **SimpleImputer (médiane)** | Remplace les valeurs manquantes par la médiane de la colonne. |
| **class_weight='balanced'** | Pondère automatiquement les classes pour compenser d'éventuels déséquilibres restants. |

---

*Projet Open Food Facts — Prédiction de l'Éco-Score*
