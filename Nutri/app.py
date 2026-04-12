import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Soutenance M1 IA - Prédiction du Nutri-Score",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #4CAF50; font-weight: 700; margin-bottom: 20px;}
    .sub-header { font-size: 1.5rem; color: #2E7D32; }
    .highlight { background-color: #f1f8e9; padding: 10px; border-radius: 5px; border-left: 5px solid #4CAF50; }
    .nutri-a { background-color: #1E8F4E; color: white; padding: 15px; text-align: center; font-size: 40px; font-weight: bold; border-radius: 10px; margin: 10px; }
    .nutri-b { background-color: #60C659; color: white; padding: 15px; text-align: center; font-size: 40px; font-weight: bold; border-radius: 10px; margin: 10px; }
    .nutri-c { background-color: #F8CC1B; color: white; padding: 15px; text-align: center; font-size: 40px; font-weight: bold; border-radius: 10px; margin: 10px; }
    .nutri-d { background-color: #EE8100; color: white; padding: 15px; text-align: center; font-size: 40px; font-weight: bold; border-radius: 10px; margin: 10px; }
    .nutri-e { background-color: #E63E11; color: white; padding: 15px; text-align: center; font-size: 40px; font-weight: bold; border-radius: 10px; margin: 10px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://static.openfoodfacts.org/images/logos/off-logo-horizontal.svg", use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Plan de la Présentation :",
    (
        "1. Contexte & Objectif",
        "2. Données & Ingénierie",
        "3. Modélisation ML",
        "4. Interprétabilité (SHAP)",
        "5. Simulateur Nutri-Score"
    )
)

st.sidebar.markdown("---")
st.sidebar.info("👨‍🎓 **Soutenance Master 1 Data & IA**\n\n*Présentation du pipeline de ML pour l'inférence du Nutri-Score.*")

# --- Logic Functions for Nutri-Score Simulator ---
def calc_points_energy(val):
    if val <= 335: return 0
    elif val > 3350: return 10
    else: return int((val - 0.0001) // 335)

def calc_points_sugar(val):
    if val <= 3.4: return 0
    elif val > 51.0: return 15
    else: return int((val - 0.0001) // 3.4)

def calc_points_sfa(val): # Acides Gras Saturés
    if val <= 1: return 0
    elif val > 10: return 10
    else: return int((val - 0.0001) // 1.0)

def calc_points_salt(val):
    if val <= 0.2: return 0
    elif val > 4.0: return 20
    else: return int((val - 0.0001) // 0.2)

def calc_points_proteins(val):
    if val <= 2.4: return 0
    elif val > 16.8: return 7
    else: return int((val - 0.0001) // 2.4)

def calc_points_fibers(val):
    if val <= 3.0: return 0
    elif val <= 4.1: return 1
    elif val <= 5.2: return 2
    elif val <= 6.3: return 3
    elif val <= 7.4: return 4
    else: return 5

def calc_points_flln(val): # Fruits, Légumes, Légumineuses
    if val <= 40: return 0
    elif val <= 60: return 1
    elif val <= 80: return 2
    else: return 5

def calc_nutriscore(energy, sugar, sfa, salt, proteins, fiber, flln):
    pt_e = calc_points_energy(energy)
    pt_su = calc_points_sugar(sugar)
    pt_sfa = calc_points_sfa(sfa)
    pt_sa = calc_points_salt(salt)
    
    total_A = pt_e + pt_su + pt_sfa + pt_sa
    
    pt_p = calc_points_proteins(proteins)
    pt_f = calc_points_fibers(fiber)
    pt_flln = calc_points_flln(flln)
    
    total_C = pt_p + pt_f + pt_flln
    
    if total_A < 11:
        score = total_A - total_C
        calc_details = f"Total A ({total_A}) < 11. Score = {total_A} - {total_C} = {score}"
    else:
        if pt_flln == 5:
            score = total_A - total_C
            calc_details = f"Total A ({total_A}) >= 11 MAIS Fruits/Légumes=5pts. Score = {total_A} - {total_C} = {score}"
        else:
            score = total_A - (pt_f + pt_flln)
            calc_details = f"Total A ({total_A}) >= 11 (Protéines ignorées). Score = {total_A} - {pt_f + pt_flln} = {score}"
            
    if score <= 0: letter = "A"
    elif score <= 2: letter = "B"
    elif score <= 10: letter = "C"
    elif score <= 18: letter = "D"
    else: letter = "E"
    
    return score, letter, calc_details, total_A, total_C


# --- PAGE 1: CONTEXTE ---
if menu == "1. Contexte & Objectif":
    st.markdown('<div class="main-header">1. Contexte du Projet</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 La base de données Open Food Facts")
        st.write("""
        Open Food Facts est une base de données collaborative, libre et ouverte sur les produits alimentaires. 
        Bien que riche (des milliers d'attributs), elle souffre de **données manquantes**, que ce soit sur les macros-nutriments, ou sur le **Nutri-Score officiel** lui-même.
        """)
        
        st.markdown("### 🎯 Objectif Machine Learning")
        st.markdown("""
        <div class="highlight">
        Construire un modèle capable de <strong>prédire le Nutri-Score</strong> sur des produits non-renseignés, à partir de leurs caractéristiques nutritionnelles et techniques (Nova, Additifs, etc.).
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.image("https://fr.openfoodfacts.org/images/misc/nutriscore-a-b-c-d-e.png", caption="Le Nutri-Score officiel en 5 grades", use_container_width=True)


# --- PAGE 2: DONNEES ---
elif menu == "2. Données & Ingénierie":
    st.markdown('<div class="main-header">2. Pipeline de Traitement des Données</div>', unsafe_allow_html=True)
    st.write("Ce projet s'articule autour de plusieurs notebooks ayant permis de nettoyer et d'enrichir la base brute d'Open Food Facts.")
    
    st.markdown("### 🔍 1. Analyse Exploratoire (`analyse_nutri.ipynb`)")
    st.write("Première étape de découverte du dataset : identification des distributions, des valeurs aberrantes et surtout, face au constat massif de **valeurs nutritives manquantes**.")

    st.markdown("### 🔗 2. Enrichissement CIQUAL (`liaison_ciqual.ipynb`)")
    st.write("Pour palier au manque de données standardisées, j'ai effectué une jointure avec la table de composition nutritionnelle **CIQUAL** (Anses) afin d'améliorer la robustesse des descriptions et des apports sur les produits.")

    st.markdown("### 🛠️ 3. Préparation & Séparation (`prepa_données.ipynb`)")
    st.write("C'est ici que le jeu de données final est scindé en deux entités distinctes : les produits *avec* Nutri-Score officiel (jeu d'entraînement/test) et les produits *sans* Nutri-Score (à prédire en inférence).")
    
    st.markdown("### 🧠 4. Imputation et Feature Engineering")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sub-header">IterativeImputer</div>', unsafe_allow_html=True)
        st.write("""
        Plutôt que d'utiliser de simples moyennes pour remplacer les valeurs nutritionnelles maquantes, j'ai utilisé une régression algorithmique : `IterativeImputer` boosté par un **ExtraTreesRegressor**.
        Cet algorithme prédit la valeur manquante d'une variable en se basant sur toutes les autres (ex: s'il manque le *Sucre*, il déduit la valeur via les *Glucides* et *l'Énergie* présents).
        """)
    with col2:
        st.markdown('<div class="sub-header">Nouvelles Variables</div>', unsafe_allow_html=True)
        st.write("""
        - **Groupe NOVA** : Intégration du degré de transformation industrielle.
        - **Additifs** : Comptage du nombre d'additifs trouvés dans le produit.
        - **Ratios Spécifiques** : (Sucre/Énergie), permettant d'aider les futurs arbres de décision à trouver des relations directes avec la santé.
        """)


# --- PAGE 3: ML ---
elif menu == "3. Modélisation ML":
    st.markdown('<div class="main-header">3. Évolution des Modèles de Classification</div>', unsafe_allow_html=True)
    st.write("La classification (en 5 classes A, B, C, D, E) s'est faite progressivement en testant différents algorithmes pour résoudre les blocages et isoler le modèle le plus performant.")
    
    col_txt, col_graph = st.columns([1.2, 1])
    
    with col_txt:
        st.markdown("### 🌱 Phase 1 : Le Modèle de Base")
        st.caption("Notebook : `prediction_nutriscore_iterative.ipynb`")
        st.write("- **Approche :** Modèle simple post-imputation.\n- **Résultat :** Environ **87.5% d'Accuracy**.\n- **Bilan :** C'était un bon démarrage, mais la variance était trop élevée, particulièrement pour les prédictions entre les classes centrales (B et C).")

        st.markdown("### 🌲 Phase 2 : Ensembles Forestiers")
        st.caption("Notebook : `prediction_nutriscore_rf.ipynb`")
        st.write("- **Approche :** Utilisation de Random Forest couplé à une Stratified K-Fold Cross-Validation pour garantir la distribution des grades.\n- **Résultat :** L'Accuracy bondit à **91.45%**.\n- **Bilan :** La robustesse est grandement améliorée sur les classes asymétriques.")

        st.markdown("### 🚀 Phase 3 : Modèles Boosting")
        st.caption("Notebooks : `prediction_nutriscore_II+XGB.ipynb` & `LGBM.ipynb`")
        st.write("- **Approche :** Implémentation de XGBoost et LightGBM, optimisés numériquement via `RandomizedSearchCV`.\n- **Résultat :** Stabilisation massive avec un **F1-macro de 91.15%** et une gestion native des valeurs manquantes.\n- **Bilan final :** Choix d'architecture optimal (Performances maximales pour des temps d'entraînement réduits).")

    with col_graph:
        # Graphique
        st.markdown("<br><br>", unsafe_allow_html=True)
        data_metrics = {
            "Modèle": ["Phase 1 (Iterative / Base)", "Phase 2 (Random Forest)", "Phase 3 (XGBoost)"],
            "Accuracy (%)": [87.54, 91.45, 91.14],
            "F1-Macro (%)": [86.39, 89.71, 91.15]
        }
        df_metrics = pd.DataFrame(data_metrics)
        
        fig = px.bar(df_metrics, x="Modèle", y=["Accuracy (%)", "F1-Macro (%)"], 
                     barmode='group', title="Progression des Performances",
                     color_discrete_sequence=['#4CAF50', '#8BC34A'])
        fig.update_yaxes(range=[80, 100])
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("---")
    report_file = "ml_exports/classification_report.csv"
    if os.path.exists(report_file):
        st.markdown("### 📊 Rapport de Classification détaillé (Jeu de Test)")
        df_report = pd.read_csv(report_file)
        st.dataframe(df_report, use_container_width=True)
    else:
        st.info("📌 Exporte ton `classification_report.csv` dans le dossier `ml_exports/` pour l'afficher dynamiquement ici.")


# --- PAGE 4: SHAP ---
elif menu == "4. Interprétabilité (SHAP)":
    st.markdown('<div class="main-header">4. Interprétabilité du modèle (SHAP)</div>', unsafe_allow_html=True)
    
    st.write("""
    Dans le domaine de la santé et de la nutrition européenne, un modèle "boîte noire" est inacceptable. 
    Nous utilisons **SHAP (SHapley Additive exPlanations)** pour déconstruire les décisions générées par le *TreeExplainer* du modèle XGBoost.
    """)
    
    st.info("💡 **Aide Visuelle** : Insédez ici vos graphiques SHAP exportés (Summary Plot, Bar Plot) depuis les notebooks.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📉 Explication globale (Feature Importance)")
        shap_file = "ml_exports/shap_summary_plot.png"
        if os.path.exists(shap_file):
            st.image(shap_file, use_container_width=True, caption="Ton SHAP Summary Plot")
        else:
            st.image("https://raw.githubusercontent.com/slundberg/shap/master/docs/artwork/shap_header.png", use_container_width=True, caption="Placeholder : Insère shap_summary_plot.png dans ml_exports/")
    
    with col2:
        st.markdown("#### 🔍 Comportement ciblé")
        st.write("""
        **Ce que SHAP nous révèle sur le Nutri-Score :**
        1. **Pénalités (Rouge)** : Des valeurs élevées en *Énergie (kJ)*, *Sucres* et *Acides Gras Saturés* augmentent exponentiellement la probabilité des classes **D et E**.
        2. **Bonus (Bleu)** : La présence importante de *Fibres* et de *Protéines* agit comme un "bouclier", poussant le modèle vers **A ou B**.
        3. **Interactions dynamiques** : Le ratio Protéines/Énergie s'est révélé être une variable clé pour l'inférence.
        """)

# --- PAGE 5: SIMULATEUR ---
elif menu == "5. Simulateur Nutri-Score":
    st.markdown('<div class="main-header">5. Simulateur "Real-Time"</div>', unsafe_allow_html=True)
    st.markdown("Algorithme répliquant les règles officielles (composante A et composante C) de façon dynamique.")
    
    with st.form("nutriscore_form"):
        st.markdown("#### 📝 Valeurs Nutritionnelles (pour 100g)")
        
        c1, c2, c3, c4 = st.columns(4)
        energy = c1.number_input("Énergie (kJ)", min_value=0, value=1200, step=100)
        sugar = c2.number_input("Sucres (g)", min_value=0.0, value=15.0, step=1.0)
        sfa = c3.number_input("Acides Gras Saturés (g)", min_value=0.0, value=5.0, step=0.5)
        salt = c4.number_input("Sel (g)", min_value=0.0, value=0.5, step=0.1)
        
        st.markdown("#### 🌱 Nutriments Positifs (pour 100g)")
        p1, p2, p3 = st.columns(3)
        proteins = p1.number_input("Protéines (g)", min_value=0.0, value=6.0, step=1.0)
        fiber = p2.number_input("Fibres (g)", min_value=0.0, value=4.0, step=1.0)
        flln = p3.number_input("Fruits Lég. Légumin. (%)", min_value=0.0, max_value=100.0, value=10.0, step=5.0)
        
        submitted = st.form_submit_button("Calculer le Nutri-Score", use_container_width=True)
        
    if submitted:
        score, letter, details, ta, tc = calc_nutriscore(energy, sugar, sfa, salt, proteins, fiber, flln)
        
        st.markdown("---")
        res_col, math_col = st.columns([1, 2])
        
        with res_col:
            st.markdown("### Résultat :")
            # Dynamic styling
            st.markdown(f'<div class="nutri-{letter.lower()}">{letter}</div>', unsafe_allow_html=True)
            st.write(f"**Score Numérique : {score}**")
            
        with math_col:
            st.markdown("### Sous-le-capot (Règles officielles)")
            st.info(f"""
            - **Points à limiter (Total A)** : {ta}
            - **Points à favoriser (Total C)** : {tc}
            """)
            st.success(f"**Mécanique de calcul :**\n{details}")
            
        # Placeholder alert indicating the ML model integration.
        st.warning("🤖 *Note M1 : À terme, on enverra ces valeurs (et d'autres features imputées) dans le modèle XGBoost `.pkl` pour comparer la prédiction du modèle avec la règle mathématique.*")
