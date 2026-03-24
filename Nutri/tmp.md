# Calcul du Nutri-Score (Mise à jour 2024 - Aliments Solides)

Le Nutri-Score se calcule pour **100g** de produit en faisant la balance entre les nutriments à limiter (Composante A) et les nutriments à favoriser (Composante C).

## 1. Composante Négative (Total A) : Les points à limiter
Calculer la somme des points correspondants à l'énergie, aux sucres, aux acides gras saturés (AGS) et au sel. 

| Points | Énergie (kJ) | Sucres totaux (g) | AGS (g) | Sel (g) |
| :---: | :--- | :--- | :--- | :--- |
| **0** | ≤ 335 | ≤ 3,4 | ≤ 1 | ≤ 0,2 |
| **1** | > 335 | > 3,4 | > 1 | > 0,2 |
| **2** | > 670 | > 6,8 | > 2 | > 0,4 |
| **3** | > 1005 | > 10,2 | > 3 | > 0,6 |
| **4** | > 1340 | > 13,6 | > 4 | > 0,8 |
| **5** | > 1675 | > 17,0 | > 5 | > 1,0 |
| **6** | > 2010 | > 20,4 | > 6 | > 1,2 |
| **7** | > 2345 | > 23,8 | > 7 | > 1,4 |
| **8** | > 2680 | > 27,2 | > 8 | > 1,6 |
| **9** | > 3015 | > 30,6 | > 9 | > 1,8 |
| **10** | > 3350 | > 34,0 | > 10 | > 2,0 |
| **11** | | > 37,4 | | > 2,2 |
| **12** | | > 40,8 | | > 2,4 |
| **13** | | > 44,2 | | > 2,6 |
| **14** | | > 47,6 | | > 2,8 |
| **15** | | > 51,0 | | > 3,0 |
| **16** | | | | > 3,2 |
| **17** | | | | > 3,4 |
| **18** | | | | > 3,6 |
| **19** | | | | > 3,8 |
| **20** | | | | > 4,0 |

*Total A = Points Énergie + Points Sucres + Points AGS + Points Sel*

---

## 2. Composante Positive (Total C) : Les points à favoriser
Calculer la somme des points correspondants aux protéines, aux fibres et à la part de fruits, légumes et légumineuses (FLLN).

| Points | Protéines (g) | Fibres (g) | Fruits, Légumes, Légumineuses (%) |
| :---: | :--- | :--- | :--- |
| **0** | ≤ 2,4 | ≤ 3,0 | ≤ 40 |
| **1** | > 2,4 | > 3,0 | > 40 |
| **2** | > 4,8 | > 4,1 | > 60 |
| **3** | > 7,2 | > 5,2 | *(Non applicable)* |
| **4** | > 9,6 | > 6,3 | *(Non applicable)* |
| **5** | > 12,0 | > 7,4 | > 80 |
| **6** | > 14,4 | | |
| **7** | > 16,8 | | |

*Total C = Points Protéines + Points Fibres + Points FLLN*

---

## 3. Calcul du Score Final

Le calcul du score final dépend du Total A obtenu à l'étape 1 :

* **Cas n°1 : Le produit a un Total A < 11**
  * **Formule :** `Score = Total A - Total C`

* **Cas n°2 : Le produit a un Total A ≥ 11**
  * *Condition 2A :* Si le produit obtient 5 points pour les Fruits, Légumes et Légumineuses.
    * **Formule :** `Score = Total A - Total C`
  * *Condition 2B :* Si le produit obtient moins de 5 points pour les Fruits, Légumes et Légumineuses (les points des protéines sont ignorés).
    * **Formule :** `Score = Total A - (Points Fibres + Points FLLN)`

---

## 4. Attribution de la lettre (Barème)

| Score Final | Nutri-Score |
| :--- | :--- |
| **≤ 0** | **A** (Vert foncé) |
| **1 à 2** | **B** (Vert clair) |
| **3 à 10** | **C** (Jaune) |
| **11 à 18** | **D** (Orange) |
| **≥ 19** | **E** (Rouge) |