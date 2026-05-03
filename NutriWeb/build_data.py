import pandas as pd
import json
import os

base_path = r'c:\Users\miste\Documents\openfoodfact\Open-Food-Fact-label'
export_path = os.path.join(base_path, 'Nutri', 'ml_exports')
output_file = os.path.join(base_path, 'NutriWeb', 'data.js')

os.makedirs(os.path.dirname(output_file), exist_ok=True)

data = {}

# 1. Learning Curves
try:
    df_loss = pd.read_csv(os.path.join(export_path, 'learning_curves.csv'))
    data['learning_curves'] = df_loss.to_dict(orient='list')
except Exception as e:
    data['learning_curves'] = {}

# 2. Confusion Matrix
try:
    df_cm = pd.read_csv(os.path.join(export_path, 'confusion_matrix.csv'), index_col=0)
    data['confusion_matrix'] = {
        'z': df_cm.values.tolist(),
        'x': df_cm.columns.tolist(),
        'y': df_cm.index.tolist()
    }
except Exception as e:
    data['confusion_matrix'] = {}

# 3. Classification Report
try:
    df_report = pd.read_csv(os.path.join(export_path, 'classification_report.csv'), index_col=0)
    # Extract overall metrics
    data['metrics'] = {
        'accuracy': float(df_report.loc['accuracy', 'precision']),
        'f1_macro': float(df_report.loc['macro avg', 'f1-score'])
    }
except Exception as e:
    data['metrics'] = {'accuracy': 0, 'f1_macro': 0}

# 4. Feature Importance
try:
    df_feat = pd.read_csv(os.path.join(export_path, 'feature_importance.csv'))
    df_feat = df_feat.sort_values(by="Importance", ascending=True)
    data['feature_importance'] = df_feat.to_dict(orient='list')
except Exception as e:
    data['feature_importance'] = {}

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("const mlData = ")
    json.dump(data, f, indent=2)
    f.write(";")
    print(f"data.js generated successfully at {output_file}")
