# 🍎 Open Food Facts — Prédiction du Nutri-Score & de l'Éco-Score

> Projet de Machine Learning appliqué à la base de données Open Food Facts pour prédire le **Nutri-Score** (santé nutritionnelle) et l'**Éco-Score** (impact environnemental) des produits alimentaires.

---

## 📋 Présentation

Ce projet s'inscrit dans le cadre d'un **Master 1 Data & IA** et explore deux problématiques complémentaires :

| Axe | Objectif | Approche |
|-----|----------|----------|
| 🥦 **Nutri-Score** | Prédire le grade nutritionnel (A–E) des produits sans score | Classification multiclasse sur données numériques |
| 🌍 **Éco-Score** | Prédire le grade environnemental (A–E) des produits sans score | Classification multiclasse via NLP (TF-IDF) |

**Source des données** : [Open Food Facts](https://world.openfoodfacts.org/) — Base de données collaborative et ouverte (~12 Go en CSV brut).

---

## 📂 Structure du projet

```
Open-Food-Fact-label/
│
├── traitement_donnees_polars.ipynb     # Extraction Nutri-Score (Polars, batch)
├── analyse_nutri_eco_scores.ipynb      # Analyse croisée Nutri/Eco
├── WORKFLOW.md                         # Documentation pipeline Nutri-Score
├── WORKFLOW_ECO.md                     # Documentation pipeline Éco-Score
│
├── Nutri/                              # 🥦 Pipeline Nutri-Score
│   ├── prepa_données.ipynb             #    Nettoyage & préparation
│   ├── prediction_nutriscore_rf.ipynb  #    Modèle V1 — Random Forest
│   ├── prediction_nutriscore_iterative.ipynb  #    Modèle V2 — RF + IterativeImputer
│   ├── prediction_nutriscore_II+LGBM.ipynb   #    Modèle V3 — LightGBM (optimisé)
│   ├── prediction_nutriscore_II+XGB.ipynb    #    Modèle V4 — XGBoost
│   ├── liaison_ciqual.ipynb            #    Liaison avec la base CIQUAL
│   ├── analyse_nutri.ipynb             #    Analyse exploratoire
│   ├── app.py                          #    Application Streamlit
│   ├── ml_exports/                     #    Exports des modèles entraînés
│   └── requirements.txt                #    Dépendances Python
│
├── eco/                                # 🌍 Pipeline Éco-Score
│   ├── traitement_donnees_ecoscore_polars.ipynb  #    Extraction (Polars, batch)
│   ├── prepa_donnees_ecoscore.ipynb    #    Nettoyage textuel (NLP)
│   ├── preparation_dataset_ecoscore.ipynb  #    Préparation alternative
│   ├── prediction_ecoscore_rf.ipynb    #    Modèle — Random Forest + TF-IDF
│   └── download_sample.py             #    Téléchargement d'échantillons via API
│
├── LabelWeb/                           # 🎨 Dashboard de soutenance (unifié)
│   ├── index.html                      #    Interface principale
│   ├── style.css                       #    Styles
│   ├── script.js                       #    Logique & graphiques Plotly
│   └── data.js                         #    Données des modèles (métriques)
│
└── NutriWeb/                           # 🎨 Dashboard Nutri-Score (legacy)
    ├── index.html
    ├── style.css
    ├── script.js
    ├── data.js
    └── build_data.py                   #    Script de génération des données
```

---

## 🥦 Nutri-Score — Pipeline

### Étape 1 · Extraction (`traitement_donnees_polars.ipynb`)
- Lecture du fichier brut (~12 Go) par **batch de 100 000 lignes** avec **Polars**
- Filtrage des produits français
- Séparation en deux jeux : **avec** Nutri-Score (entraînement) et **sans** Nutri-Score (prédiction)

### Étape 2 · Nettoyage (`Nutri/prepa_données.ipynb`)
- Sélection de 15 colonnes utiles
- Typage numérique, suppression des aberrations
- Plafonnement des valeurs à 100g, cohérence sucres/glucides

### Étape 3 · Modélisation
Trois modèles par ordre croissant de sophistication :

| Modèle | Imputation | Classifieur | Accuracy | F1-macro |
|--------|------------|-------------|----------|----------|
| **V1** | Médiane | Random Forest | ~90.7% | ~89.7% |
| **V2** | IterativeImputer | Random Forest | ↗ | ↗ |
| **V3** | IterativeImputer | LightGBM + HPO | 🏆 best | 🏆 best |

> **Features clés** : énergie, sucres, graisses saturées, sel, fibres, protéines, fruits/légumes, + ratios dérivés (sugars_ratio, sat_fat_ratio), NOVA, additifs.

---

## 🌍 Éco-Score — Pipeline

### Étape 1 · Extraction (`eco/traitement_donnees_ecoscore_polars.ipynb`)
- Même logique de batch Polars, adaptée aux colonnes textuelles
- Équilibrage des classes (grades a–e) lors de l'extraction

### Étape 2 · Nettoyage NLP (`eco/prepa_donnees_ecoscore.ipynb`)
- Nettoyage textuel : minuscules, suppression des retours à la ligne
- Remplacement des NaN par des chaînes vides

### Étape 3 · Modélisation (`eco/prediction_ecoscore_rf.ipynb`)
- **TF-IDF** sur `categories` (100 features) et `ingredients_text` (200 features)
- **ColumnTransformer** combinant traitement textuel et numérique
- **Random Forest** avec `class_weight='balanced'`

> **Spécificité** : L'Éco-Score repose sur le **texte** (ingrédients, catégories, labels, packaging) plutôt que sur les macros nutritionnelles.

---

## 🎨 Dashboard de Soutenance

Le dossier `LabelWeb/` contient un **dashboard interactif** (HTML/CSS/JS + Plotly) couvrant les deux axes du projet :

- **Sections I–VII** : Nutri-Score (contexte, collecte, ingénierie, évaluation, SHAP, simulateur, annexe)
- **Sections VIII–XIV** : Éco-Score (contexte, collecte NLP, ingénierie TF-IDF, évaluation, SHAP, simulateur, annexe)

Pour le lancer : ouvrir `LabelWeb/index.html` dans un navigateur.

---

## ⚙️ Prérequis & Installation

### Python
```bash
python >= 3.9
```

### Dépendances
```bash
pip install -r Nutri/requirements.txt
pip install polars   # Pour les notebooks d'extraction
```

### Principales bibliothèques

| Catégorie | Bibliothèques |
|-----------|---------------|
| Data | `pandas`, `numpy`, `polars` |
| ML | `scikit-learn`, `xgboost`, `lightgbm` |
| Interprétabilité | `shap` |
| Visualisation | `plotly`, `matplotlib` |
| Interface | `streamlit` |
| Dev | `jupyter`, `ipykernel` |

---

## 🚀 Utilisation

### 1. Extraction des données
```bash
# Exécuter le notebook d'extraction (nécessite data_brut.csv ~12 Go)
jupyter notebook traitement_donnees_polars.ipynb
```

### 2. Entraînement Nutri-Score
```bash
jupyter notebook Nutri/prepa_données.ipynb
jupyter notebook Nutri/prediction_nutriscore_II+LGBM.ipynb  # Meilleur modèle
```

### 3. Entraînement Éco-Score
```bash
jupyter notebook eco/prepa_donnees_ecoscore.ipynb
jupyter notebook eco/prediction_ecoscore_rf.ipynb
```

### 4. Application Streamlit (Nutri-Score)
```bash
cd Nutri
streamlit run app.py
```

### 5. Dashboard de soutenance
Ouvrir directement `LabelWeb/index.html` dans un navigateur.

---

## 📖 Documentation détaillée

- [WORKFLOW.md](WORKFLOW.md) — Pipeline complet du Nutri-Score (étapes, features, modèles, glossaire)
- [WORKFLOW_ECO.md](WORKFLOW_ECO.md) — Pipeline complet de l'Éco-Score (NLP, TF-IDF, modèle)

---

## 📜 Licence

Les données utilisées proviennent de la base [Open Food Facts](https://world.openfoodfacts.org/), disponible sous licence [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/1.0/).

---

*Projet Master 1 Data & IA — Soutenance de Projet*
