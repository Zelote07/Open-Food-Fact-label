const mlData = {
  "nutri": {
    "learning_curves": {
      "epoch": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
      "train_loss": [1.5, 1.1, 0.8, 0.6, 0.45, 0.35, 0.28, 0.23, 0.19, 0.16, 0.14],
      "val_loss": [1.55, 1.18, 0.85, 0.65, 0.52, 0.43, 0.37, 0.33, 0.30, 0.28, 0.27]
    },
    "metrics": { "accuracy": 0.865, "f1_macro": 0.868, "log_loss": 0.27 },
    "feature_importance": {
      "Importance": [0.05, 0.10, 0.15, 0.25, 0.30, 0.55, 0.75, 1.2, 2.5],
      "Feature": ["Sel", "Fibres", "Protéines", "Glucides", "Score_NOVA", "Graisses Saturées", "Sucres", "Énergie", "Energy (kJ)"]
    }
  },
  "eco": {
    "learning_curves": {
      "epoch": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
      "train_loss": [1.4, 1.1, 0.8, 0.5, 0.3, 0.2, 0.15, 0.1, 0.08, 0.06, 0.05],
      "val_loss": [1.45, 1.2, 0.9, 0.65, 0.5, 0.45, 0.42, 0.4, 0.39, 0.38, 0.38]
    },
    "metrics": { "accuracy": 0.824, "f1_macro": 0.812, "log_loss": 0.38 },
    "feature_importance": {
      "Importance": [0.02, 0.08, 0.15, 0.25, 0.40, 0.60, 0.90, 1.4, 2.8],
      "Feature": ["cat_sucre", "ing_sel", "ing_arôme", "cat_poisson", "ing_lait", "cat_viande", "ing_palme", "ing_bio", "cat_légume"]
    }
  }
};
