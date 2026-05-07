import requests
import csv
import pandas as pd

def download_subset():
    url = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv"
    output_path = "dataset_openfoodfacts_ecoscore.csv"
    
    headers = {
        "User-Agent": "EcoScoreMLProject/1.1 - Python Script (User Download)"
    }
    response = requests.get(url, stream=True, headers=headers)
    response.raise_for_status()
    
    # generateur de lignes decodées
    lines = (line.decode('utf-8', errors='ignore') for line in response.iter_lines())
    
    # extraction de l'entete
    reader = csv.DictReader(lines, delimiter='\t')
    
    desired_columns = [
        "code", "product_name", "nutriscore_grade", "ecoscore_score", "ecoscore_grade",
        "categories", "labels", "packaging", "origins", "ingredients_text", "ingredients_analysis_tags"
    ]
    
    collected = []
    print("Recherche de 5000 produits avec un éco-score valide...")
    
    for count, row in enumerate(reader):
        eco = row.get("ecoscore_grade", "")
        if eco and isinstance(eco, str) and eco.lower() not in ["", "unknown", "not-applicable"]:
            item = {col: row.get(col, "") for col in desired_columns}
            collected.append(item)
            
            if len(collected) >= 5000:
                print(f"5000 produits trouvés après avoir parcouru {count} lignes.")
                break
                
        if count > 0 and count % 50000 == 0:
            print(f"{count} lignes parcourues, {len(collected)} produits valides trouvés...")
            
    response.close()
    
    df = pd.DataFrame(collected)
    df.to_csv(output_path, index=False)
    print(f"Dataset exporté vers : {output_path}")

if __name__ == '__main__':
    download_subset()
