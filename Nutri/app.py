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

# --- CSS CUSTOM & THEME PREMIUM ---
st.markdown("""
<style>
    /* Import de la police Inter pour un look plus moderne */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* En-têtes de page */
    .main-header { 
        font-size: 2.8rem; 
        color: #1E293B; 
        font-weight: 700; 
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }
    
    .sub-header { 
        font-size: 1.2rem; 
        color: #64748B; 
        font-weight: 400; 
        margin-bottom: 30px;
    }

    /* Cartes de KPI / Info */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #E2E8F0;
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.05);
    }
    
    .metric-title {
        color: #64748B;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        color: #0F172A;
        font-size: 2.2rem;
        font-weight: 700;
        margin-top: 10px;
    }

    /* Mise en évidence (Highlight) */
    .highlight-card { 
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 25px; 
        border-radius: 12px; 
        border-left: 6px solid #22c55e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .highlight-card strong {
        color: #166534;
        font-size: 1.1rem;
    }

    /* Badges Nutri-Score */
    .nutri-badge {
        display: inline-block;
        color: white;
        padding: 20px 40px;
        text-align: center;
        font-size: 60px;
        font-weight: 800;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .nutri-a { background: linear-gradient(135deg, #1E8F4E 0%, #146B38 100%); }
    .nutri-b { background: linear-gradient(135deg, #60C659 0%, #4CAF50 100%); }
    .nutri-c { background: linear-gradient(135deg, #F8CC1B 0%, #F5B041 100%); }
    .nutri-d { background: linear-gradient(135deg, #EE8100 0%, #D35400 100%); }
    .nutri-e { background: linear-gradient(135deg, #E63E11 0%, #C0392B 100%); }

</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://static.openfoodfacts.org/images/logos/off-logo-horizontal.svg", use_container_width=True)
    st.markdown("---")
    
    st.markdown("### 🧭 Navigation")
    menu = st.radio(
        "",
        (
            "1️⃣ Contexte & Objectif",
            "2️⃣ Données & Ingénierie",
            "3️⃣ Modélisation ML",
            "4️⃣ Interprétabilité (SHAP)",
            "5️⃣ Simulateur Nutri-Score"
        ),
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;">
        <h4 style="margin-top: 0; color: #334155;">🎓 Master 1 Data & IA</h4>
        <p style="font-size: 0.9em; color: #64748B; margin-bottom: 0;">Soutenance de projet : Prédiction et Inférence du Nutri-Score via Machine Learning.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Logic Functions for Nutri-Score Simulator ---
def calc_points_energy(val):
    if val <= 335: return 0
    elif val > 3350: return 10
    else: return int((val - 0.0001) // 335)

def calc_points_sugar(val):
    if val <= 3.4: return 0
    elif val > 51.0: return 15
    else: return int((val - 0.0001) // 3.4)

def calc_points_sfa(val):
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

def calc_points_flln(val):
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


# ==============================================================================
# --- PAGE 1: CONTEXTE ---
# ==============================================================================
if menu == "1️⃣ Contexte & Objectif":
    st.markdown('<div class="main-header">Contexte & Objectif</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pourquoi l\'Intelligence Artificielle au service de la nutrition ?</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### 📊 La base de données Open Food Facts")
        st.write("""
        **Open Food Facts** est une base de données collaborative colossale recensant des centaines de milliers de produits alimentaires à travers le monde.
        Cependant, en tant que projet participatif, elle souffre d'un problème majeur : la **complétude des données**.
        """)
        
        st.info("💡 **Problème :** De nombreux produits n'ont pas leurs macros-nutriments complets, et une grande proportion n'affiche pas de Nutri-Score officiel.")
        
        st.markdown("### 🎯 Notre Mission (Machine Learning)")
        st.markdown("""
        <div class="highlight-card">
            <strong>Objectif Principal :</strong><br><br>
            Concevoir, entraîner et valider un algorithme de Machine Learning capable de :<br>
            1. <strong>Imputer</strong> de manière intelligente les valeurs nutritionnelles manquantes.<br>
            2. <strong>Prédire</strong> avec précision le Nutri-Score (A, B, C, D, E) d'un produit, même avec des données partielles.
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.image("https://fr.openfoodfacts.org/images/misc/nutriscore-a-b-c-d-e.png", use_container_width=True)
        st.markdown("""
        <div style="text-align: center; color: #64748B; font-size: 0.9em; margin-top: 10px;">
            Le Nutri-Score, un label de santé publique européen à 5 classes.
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# --- PAGE 2: DONNEES ---
# ==============================================================================
elif menu == "2️⃣ Données & Ingénierie":
    st.markdown('<div class="main-header">Données & Ingénierie</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Du nettoyage brut à la création de features intelligentes</div>', unsafe_allow_html=True)
    
    # Timeline like structure
    with st.container():
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown("### 🔍 Étape 1<br><span style='color: #64748B; font-size: 0.8em;'>Analyse Exploratoire</span>", unsafe_allow_html=True)
        with c2:
            st.info("Découverte du dataset `analyse_nutri.ipynb` : Analyse des distributions, traitement des valeurs aberrantes (outliers) et identification du volume massif de valeurs manquantes (NaNs).")
            
    with st.container():
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown("### 🔗 Étape 2<br><span style='color: #64748B; font-size: 0.8em;'>Enrichissement CIQUAL</span>", unsafe_allow_html=True)
        with c2:
            st.info("Jointure avec la base **CIQUAL (Anses)** (`liaison_ciqual.ipynb`). Cette étape a permis de combler de nombreuses lacunes grâce à des données standardisées gouvernementales, solidifiant la base de nos macros-nutriments.")

    st.markdown("---")
    
    st.markdown("### 🧠 Modélisation Imputative et Feature Engineering")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align: left; height: 100%;">
            <div class="metric-title" style="color: #2563EB;">L'Algorithme IterativeImputer</div>
            <p style="margin-top: 15px; color: #334155;">Plutôt que d'utiliser de simples moyennes (imprécises en nutrition), nous avons déployé un <b>IterativeImputer</b> propulsé par un <i>ExtraTreesRegressor</i>.</p>
            <p style="color: #64748B; font-size: 0.9em;">Il prédit la valeur manquante d'une variable en se basant sur toutes les autres (ex: si le <i>Sucre</i> est manquant, le modèle le déduit via les <i>Glucides</i> et <i>l'Énergie</i> présents).</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="metric-card" style="text-align: left; height: 100%;">
            <div class="metric-title" style="color: #16A34A;">Nouvelles Variables (Features)</div>
            <ul style="margin-top: 15px; color: #334155; padding-left: 20px;">
                <li><b>Score NOVA :</b> Intégration du degré de transformation ultra-industrielle.</li>
                <li><b>Additifs :</b> Comptage dynamique du nombre d'additifs chimiques.</li>
                <li><b>Ratios Spécifiques :</b> Création de features expertes comme <i>Sucre/Énergie</i> pour aider les arbres de décisions à isoler les signaux faibles.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# --- PAGE 3: ML ---
# ==============================================================================
elif menu == "3️⃣ Modélisation ML":
    st.markdown('<div class="main-header">Modélisation Machine Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tableau de bord des performances du modèle final (XGBoost)</div>', unsafe_allow_html=True)
    
    # Load mock data
    try:
        df_loss = pd.read_csv("ml_exports/learning_curves.csv")
        df_cm = pd.read_csv("ml_exports/confusion_matrix.csv", index_col=0)
        df_report = pd.read_csv("ml_exports/classification_report.csv", index_col=0)
        has_data = True
    except FileNotFoundError:
        st.error("⚠️ Fichiers d'export manquants dans `ml_exports/`. Lance tes scripts Python ou utilise les mocks générés.")
        has_data = False

    if has_data:
        # --- KPIs ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        acc = df_report.loc['accuracy', 'precision'] * 100
        f1_macro = df_report.loc['macro avg', 'f1-score'] * 100
        
        kpi1.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Accuracy Globale</div>
            <div class="metric-value" style="color: #10B981;">{acc:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        kpi2.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">F1-Score (Macro)</div>
            <div class="metric-value" style="color: #3B82F6;">{f1_macro:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        kpi3.markdown("""
        <div class="metric-card">
            <div class="metric-title">Modèle Final</div>
            <div class="metric-value" style="color: #8B5CF6; font-size: 1.8rem; margin-top: 15px;">XGBoost</div>
        </div>
        """, unsafe_allow_html=True)
        
        kpi4.markdown("""
        <div class="metric-card">
            <div class="metric-title">Validation</div>
            <div class="metric-value" style="color: #F59E0B; font-size: 1.8rem; margin-top: 15px;">K-Fold (5)</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- CHARTS ---
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### 📈 Courbes d'Apprentissage (Loss)")
            fig_loss = go.Figure()
            fig_loss.add_trace(go.Scatter(x=df_loss['epoch'], y=df_loss['train_loss'], mode='lines', name='Train Loss', line=dict(color='#3B82F6', width=3)))
            fig_loss.add_trace(go.Scatter(x=df_loss['epoch'], y=df_loss['val_loss'], mode='lines', name='Validation Loss', line=dict(color='#F59E0B', width=3)))
            fig_loss.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_loss.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E2E8F0')
            fig_loss.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E2E8F0')
            st.plotly_chart(fig_loss, use_container_width=True)

        with col_chart2:
            st.markdown("### 🎯 Matrice de Confusion")
            fig_cm = px.imshow(
                df_cm.values, 
                labels=dict(x="Classe Prédite", y="Classe Réelle", color="Nombre d'observations"),
                x=df_cm.columns, y=df_cm.index,
                color_continuous_scale='Blues',
                text_auto=True
            )
            fig_cm.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig_cm, use_container_width=True)

        # --- REPORT TABLE ---
        st.markdown("---")
        st.markdown("### 📋 Rapport de Classification Détaillé")
        
        # Format the dataframe to look nice
        df_display = df_report.copy()
        for col in ['precision', 'recall', 'f1-score']:
            df_display[col] = (df_display[col] * 100).apply(lambda x: f"{x:.1f}%")
        df_display['support'] = df_display['support'].astype(int)
        
        st.dataframe(
            df_display.style.background_gradient(cmap='Greens', subset=['precision', 'recall', 'f1-score']),
            use_container_width=True
        )

# ==============================================================================
# --- PAGE 4: SHAP ---
# ==============================================================================
elif menu == "4️⃣ Interprétabilité (SHAP)":
    st.markdown('<div class="main-header">Interprétabilité des Décisions</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ouvrir la boîte noire de l\'IA avec les valeurs SHAP (SHapley Additive exPlanations)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size: 1.1rem; color: #475569; margin-bottom: 20px;">
        Dans le domaine de la santé et de la nutrition, un modèle "boîte noire" est inacceptable. 
        Nous utilisons <strong>SHAP</strong> pour déconstruire les décisions générées par notre modèle XGBoost et comprendre exactement <em>pourquoi</em> un produit reçoit la note A ou E.
    </div>
    """, unsafe_allow_html=True)
    
    try:
        df_feat = pd.read_csv("ml_exports/feature_importance.csv")
        df_feat = df_feat.sort_values(by="Importance", ascending=True) # Ascending for horizontal bar chart
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.markdown("### 📊 Importance Globale des Variables")
            fig_shap = px.bar(
                df_feat, x="Importance", y="Feature", orientation='h',
                color="Importance", color_continuous_scale="Viridis"
            )
            fig_shap.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False
            )
            fig_shap.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E2E8F0')
            st.plotly_chart(fig_shap, use_container_width=True)
            
        with col2:
            st.markdown("### 🧠 Ce que SHAP nous révèle")
            
            with st.expander("🚨 Pénalités (Tendance vers D et E)", expanded=True):
                st.write("""
                Des valeurs élevées en **Énergie (kJ)**, **Sucres** et **Acides Gras Saturés** augmentent de façon drastique la probabilité que le modèle classe le produit en **D** ou **E**. L'algorithme a parfaitement internalisé les règles de la composante "A" du score.
                """)
                
            with st.expander("🛡️ Boucliers (Tendance vers A et B)", expanded=True):
                st.write("""
                La présence importante de **Fibres** et de **Protéines** agit comme un bouclier mathématique. Le modèle accorde un poids énorme à ces features pour rattraper un score qui aurait pu être pénalisé par l'énergie.
                """)
                
            with st.expander("🔬 Interactions Dynamiques", expanded=True):
                st.write("""
                Le modèle a découvert seul que le ratio **Protéines/Énergie** était discriminant. L'utilisation de notre feature synthétique `Score_Nova` s'avère également avoir un impact subtil mais définitif sur les cas tangents entre la classe B et C.
                """)

        # Si l'utilisateur a généré la vraie image SHAP de son notebook
        shap_img = "ml_exports/shap_summary_plot.png"
        if os.path.exists(shap_img):
            st.markdown("---")
            st.markdown("### 📉 SHAP Summary Plot (Détails de distribution)")
            st.image(shap_img, use_container_width=True)

    except FileNotFoundError:
        st.error("⚠️ Fichier `feature_importance.csv` introuvable. Veuillez générer les données mock.")

# ==============================================================================
# --- PAGE 5: SIMULATEUR ---
# ==============================================================================
elif menu == "5️⃣ Simulateur Nutri-Score":
    st.markdown('<div class="main-header">Simulateur Interactif</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Calculez le Nutri-Score en temps réel via l\'algorithme officiel</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # UI Layout with columns and cards
    col_input, col_result = st.columns([2, 1.2])
    
    with col_input:
        with st.form("nutriscore_form"):
            st.markdown("<h3 style='color: #E63E11;'>🚨 À limiter (Composante A)</h3>", unsafe_allow_html=True)
            st.write("Valeurs nutritionnelles pour 100g ou 100ml :")
            
            c1, c2 = st.columns(2)
            energy = c1.number_input("⚡ Énergie (kJ)", min_value=0, value=1200, step=100)
            sugar = c2.number_input("🍬 Sucres (g)", min_value=0.0, value=15.0, step=1.0)
            sfa = c1.number_input("🧈 Acides Gras Saturés (g)", min_value=0.0, value=5.0, step=0.5)
            salt = c2.number_input("🧂 Sel (g)", min_value=0.0, value=0.5, step=0.1)
            
            st.markdown("<br><h3 style='color: #1E8F4E;'>🌱 À favoriser (Composante C)</h3>", unsafe_allow_html=True)
            
            p1, p2, p3 = st.columns(3)
            proteins = p1.number_input("🥩 Protéines (g)", min_value=0.0, value=6.0, step=1.0)
            fiber = p2.number_input("🌾 Fibres (g)", min_value=0.0, value=4.0, step=1.0)
            flln = p3.number_input("🍎 Fruits, Légumes (%)", min_value=0.0, max_value=100.0, value=10.0, step=5.0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Calculer le Nutri-Score 🚀", use_container_width=True)
            
    with col_result:
        st.markdown("### Résultat de l'Inférence")
        
        if submitted:
            score, letter, details, ta, tc = calc_nutriscore(energy, sugar, sfa, salt, proteins, fiber, flln)
            
            st.markdown(f"""
            <div style="text-align: center; margin-top: 20px; margin-bottom: 30px;">
                <div class="nutri-badge nutri-{letter.lower()}">{letter}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Score Numérique Final</div>
                <div class="metric-value" style="color: #334155;">{score}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🔍 Voir le détail du calcul officiel"):
                st.markdown(f"""
                - **Points Négatifs (Total A) :** {ta} points
                - **Points Positifs (Total C) :** {tc} points
                """)
                st.info(f"**Règle appliquée :**\n{details}")
                
            st.markdown("""
            <div style="margin-top: 20px; font-size: 0.85em; color: #64748B; padding: 10px; background-color: #f8fafc; border-radius: 8px;">
                🤖 <i>Note : Dans l'application finale, ces inputs alimenteront directement le modèle XGBoost (.pkl) exporté, permettant de comparer la prédiction du modèle de Machine Learning avec la règle mathématique.</i>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div style="height: 300px; display: flex; align-items: center; justify-content: center; border: 2px dashed #CBD5E1; border-radius: 15px; background-color: #F8FAFC;">
                <p style="color: #94A3B8; text-align: center;">Remplissez les valeurs à gauche<br>et cliquez sur Calculer</p>
            </div>
            """, unsafe_allow_html=True)
