# Dossier d'Export des Résultats Machine Learning

Ce dossier `ml_exports` est destiné à accueillir les résultats bruts et les graphiques exportés depuis tes notebooks d'entraînement (XGBoost, LightGBM, Random Forest). 

L'application Streamlit ira chercher ces fichiers pour les afficher dynamiquement dans ta soutenance.

## Fichiers attendus à exporter depuis tes notebooks :

### 1. Courbes d'Apprentissage (Loss / Accuracy)
* **`learning_curves.csv`** : Un fichier CSV ou tu auras sauvegardé l'évolution de la fonction de perte (Loss) et de la précision (Accuracy) sur tes jeux de *train* et de *validation* pour chaque époque/itération de ton meilleur modèle (ex: XGBoost). 
  * *Colonnes attendues : `epoch`, `train_loss`, `val_loss`, `train_accuracy`, `val_accuracy`*

### 2. Matrice de Confusion
* **`confusion_matrix.csv`** : Le résultat de `confusion_matrix(y_true, y_pred)`.
* *Ou au format image* : **`confusion_matrix.png`** (Si tu as utilisé Seaborn/Matplotlib pour la générer visuellement, sauvegarde-la avec `plt.savefig("confusion_matrix.png")`).

### 3. Rapport de Classification
* **`classification_report.csv`** : Exporte le résultat de `classification_report` (de Scikit-learn) au format CSV pour l'afficher sous forme de beau tableau interactif dans Streamlit.

### 4. Visuels SHAP (Interprétabilité)
* **`shap_summary_plot.png`** : Le fameux résumé des variables (impact et direction). *(Exporté via `shap.summary_plot(..., show=False)` puis `plt.savefig(...)`)*.
* **`shap_bar_plot.png`** : Le diagramme en bâtons montrant l'importance absolue moyenne des features.

---

### Comment faire l'exportation dans tes notebooks ? (Exemple rapide)

#### Pour la courbe de Loss (XGBoost) :
```python
results = model.evals_result()
epochs = len(results['validation_0']['mlogloss'])
df_loss = pd.DataFrame({
    'epoch': range(epochs),
    'train_loss': results['validation_0']['mlogloss'],
    'val_loss': results['validation_1']['mlogloss']
})
df_loss.to_csv('ml_exports/learning_curves.csv', index=False)
```

#### Pour les images SHAP :
```python
import matplotlib.pyplot as plt
shap.summary_plot(shap_values, X_test, show=False)
plt.savefig('ml_exports/shap_summary_plot.png', bbox_inches='tight')
plt.close()
```
