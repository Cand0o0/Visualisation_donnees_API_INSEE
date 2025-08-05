import streamlit as st
import plotly.graph_objects as go
from insee_bdm_api import InseeBdmAPI
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import warnings

# Supprimer les warnings de dépréciation
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Configuration de la page
st.set_page_config(
    page_title="Visualisation des données INSEE",
    page_icon="📊",
    layout="wide"
)

# Authentification
def check_authentication():
    """Vérifie l'authentification de l'utilisateur"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Authentification")
        st.markdown("---")
        
        # Formulaire de connexion
        with st.form("login_form"):
            username = st.text_input("Identifiant")
            password = st.text_input("Mot de passe", type="password")
            submit_button = st.form_submit_button("Se connecter")
            
            if submit_button:
                # Utiliser les secrets Streamlit
                correct_username = st.secrets.authentication.username
                correct_password = st.secrets.authentication.password
                
                if username == correct_username and password == correct_password:
                    st.session_state.authenticated = True
                    st.success("✅ Connexion réussie !")
                    st.rerun()
                else:
                    st.error("❌ Identifiant ou mot de passe incorrect")
        
        st.stop()

# Vérifier l'authentification
check_authentication()

# Fonctions de sauvegarde et chargement des séries
def save_series_to_json(series_dict: dict, filename: str = "saved_series.json"):
    """Sauvegarde les séries dans un fichier JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(series_dict, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {str(e)}")
        return False

def load_series_from_json(filename: str = "saved_series.json") -> dict:
    """Charge les séries depuis un fichier JSON"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Retourne les séries par défaut si le fichier n'existe pas
            return {
                "Population française": "001641607",
                "Indice des prix à la consommation": "001769682",
                "Taux de chômage": "001688526"
            }
    except Exception as e:
        st.error(f"Erreur lors du chargement : {str(e)}")
        # Retourne les séries par défaut en cas d'erreur
        return {
            "Population française": "001641607",
            "Indice des prix à la consommation": "001769682",
            "Taux de chômage": "001688526"
        }

# Titre de l'application
st.title("📊 Visualisation des données INSEE")

# Initialisation de la session state
if 'api' not in st.session_state:
    try:
        # Utiliser les secrets Streamlit pour l'API INSEE
        consumer_key = st.secrets.insee_api.consumer_key
        consumer_secret = st.secrets.insee_api.consumer_secret
        st.session_state.api = InseeBdmAPI(consumer_key, consumer_secret)
    except Exception as e:
        st.error(f"Erreur lors de la lecture des secrets : {str(e)}")
        st.stop()

# Initialisation du dictionnaire des séries dans la session state
if 'series_options' not in st.session_state:
    st.session_state.series_options = load_series_from_json()

# Fonction pour mettre à jour les séries et sauvegarder
def update_series_and_save(new_series_dict: dict):
    """Met à jour les séries et les sauvegarde"""
    st.session_state.series_options = new_series_dict
    save_series_to_json(new_series_dict)

# Sidebar pour les contrôles
st.sidebar.header("Paramètres")

# Gestion des séries (ajout/suppression)
with st.sidebar.expander("⚙️ Gérer les séries", expanded=False):
    # Onglets pour séparer l'ajout et la suppression
    tab_add, tab_search, tab_delete = st.tabs(["Ajouter", "Rechercher", "Supprimer"])
    
    # Onglet Ajout manuel
    with tab_add:
        with st.form("add_series"):
            new_series_name = st.text_input("Nom de la série")
            new_series_id = st.text_input("IdBank de la série")
            
            # Bouton pour tester l'IdBank
            test_submitted = st.form_submit_button("Tester l'IdBank")
            if test_submitted and new_series_id:
                # Test de l'IdBank
                test_result = st.session_state.api.get_series_by_idbank(new_series_id)
                if "error" in test_result:
                    st.error("❌ IdBank invalide ou série non trouvée")
                else:
                    st.success(f"✅ Série trouvée : {test_result['metadata']['TITLE_FR']}")
                    # Pré-remplir le nom si non fourni
                    if not new_series_name:
                        new_series_name = test_result['metadata']['TITLE_FR']
            
            # Bouton pour ajouter la série
            submitted = st.form_submit_button("Ajouter la série")
            if submitted and new_series_name and new_series_id:
                # Vérification de l'IdBank
                test_result = st.session_state.api.get_series_by_idbank(new_series_id)
                if "error" in test_result:
                    st.error("❌ IdBank invalide ou série non trouvée")
                else:
                    # Ajout de la série et sauvegarde
                    new_series_dict = st.session_state.series_options.copy()
                    new_series_dict[new_series_name] = new_series_id
                    update_series_and_save(new_series_dict)
                    st.success(f"✅ Série '{new_series_name}' ajoutée avec succès !")
    
    # Onglet Recherche
    with tab_search:
        search_query = st.text_input("🔍 Rechercher une série", 
                                   placeholder="Entrez un mot-clé (ex: population, prix, emploi...)")
        
        if search_query:
            with st.spinner("Recherche en cours..."):
                search_results = st.session_state.api.search_series(search_query)
                
                if isinstance(search_results, list):
                    st.write(f"📊 {len(search_results)} séries trouvées")
                    
                    # Affichage des résultats dans un tableau
                    for serie in search_results:
                        with st.expander(f"📈 {serie['title_fr']} ({serie['idbank']})"):
                            st.write(f"**Unité** : {serie['unit']}")
                            st.write(f"**Fréquence** : {serie['frequency']}")
                            
                            # Bouton pour ajouter la série
                            if st.button("➕ Ajouter cette série", key=f"add_{serie['idbank']}"):
                                new_series_dict = st.session_state.series_options.copy()
                                new_series_dict[serie['title_fr']] = serie['idbank']
                                update_series_and_save(new_series_dict)
                                st.success("✅ Série ajoutée avec succès !")
                                st.rerun()
                else:
                    st.error("❌ Erreur lors de la recherche")
    
    # Onglet Suppression
    with tab_delete:
        st.write("Sélectionnez les séries à supprimer :")
        series_to_delete = []
        
        # Création des cases à cocher pour chaque série
        for series_name in st.session_state.series_options.keys():
            if st.checkbox(f"🗑️ {series_name}", key=f"delete_{series_name}"):
                series_to_delete.append(series_name)
        
        # Bouton de suppression
        if st.button("Supprimer les séries sélectionnées"):
            if series_to_delete:
                new_series_dict = st.session_state.series_options.copy()
                for series_name in series_to_delete:
                    del new_series_dict[series_name]
                update_series_and_save(new_series_dict)
                st.success(f"✅ {len(series_to_delete)} série(s) supprimée(s)")
                st.rerun()
            else:
                st.warning("Aucune série sélectionnée pour la suppression")

# Liste des séries disponibles
st.sidebar.subheader("Séries disponibles")
selected_series = st.sidebar.selectbox(
    "Choisir une série",
    list(st.session_state.series_options.keys())
)

# Sélection de la période
current_year = datetime.now().year
start_year = st.sidebar.slider(
    "Année de début",
    min_value=1990,
    max_value=current_year,
    value=current_year-5
)

# Récupération des données
try:
    idbank = st.session_state.series_options[selected_series]
    result = st.session_state.api.get_series_by_idbank(
        idbank,
        start_period=f"{start_year}-01"
    )

    if "error" in result:
        st.error(f"Erreur lors de la récupération des données : {result['error']}")
    else:
        # Création du DataFrame
        df = pd.DataFrame(result['observations'])
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['valeur'] = pd.to_numeric(df['valeur'])
            
            # Affichage des métadonnées
            st.subheader("📋 Informations sur la série")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Titre** : {result['metadata']['TITLE_FR']}")
            with col2:
                st.info(f"**Unité** : {result['metadata']['UNIT_MEASURE']}")
            
            # Création du graphique avec Plotly
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['valeur'],
                mode='lines+markers',
                name=selected_series,
                line=dict(width=2),
                marker=dict(size=6)
            ))
            
            # Personnalisation du graphique
            fig.update_layout(
                title={
                    'text': f"Évolution de {selected_series}",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis_title="Date",
                yaxis_title=f"Valeur ({result['metadata']['UNIT_MEASURE']})",
                hovermode='x unified',
                template='plotly_white'
            )
            
            # Affichage du graphique
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau des dernières valeurs
            st.subheader("📊 Dernières valeurs")
            last_values = df.tail(12).copy()
            last_values['date'] = last_values['date'].dt.strftime('%Y-%m')
            last_values = last_values[['date', 'valeur']]
            last_values.columns = ['Date', 'Valeur']
            st.dataframe(last_values, hide_index=True)
        else:
            st.warning("Aucune donnée disponible pour la période sélectionnée")

except Exception as e:
    st.error(f"Une erreur est survenue : {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Données fournies par l'INSEE via l'API BDM*")