import streamlit as st
from insee_bdm_api import InseeBdmAPI
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import re

# Configuration de la page
st.set_page_config(
    page_title="Explorateur des séries INSEE",
    page_icon="🔍",
    layout="wide"
)

# Initialisation des états de session
if 'api' not in st.session_state:
    try:
        with open('insee api.txt', 'r') as f:
            lines = f.readlines()
            consumer_key = lines[7].split(': ')[1].strip()
            consumer_secret = lines[8].split(': ')[1].strip()
            st.session_state.api = InseeBdmAPI(consumer_key, consumer_secret)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier de configuration : {str(e)}")
        st.stop()

if 'all_dataflows' not in st.session_state:
    st.session_state.all_dataflows = None
if 'selected_dataflow' not in st.session_state:
    st.session_state.selected_dataflow = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'api_calls' not in st.session_state:
    st.session_state.api_calls = []

# Titre de la page
st.title("🔍 Explorateur des séries INSEE")

# Zone de debug pour les appels API
with st.expander("🔍 Détails des appels API", expanded=True):
    for call in st.session_state.api_calls:
        st.code(call)

def normalize_search_term(term: str) -> str:
    """Normalise le terme de recherche"""
    if not term:
        return ""
    term = term.lower()
    term = term.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    term = term.replace('à', 'a').replace('â', 'a')
    term = term.replace('ô', 'o')
    term = term.replace('û', 'u').replace('ù', 'u')
    term = term.replace('î', 'i')
    term = re.sub(r'[^a-z0-9\s]', '', term)
    return term

def get_all_dataflows() -> list:
    """Récupère tous les dataflows disponibles"""
    try:
        url = "https://api.insee.fr/series/BDM/V1/dataflow"
        st.session_state.api_calls.append(f"GET {url}")
        
        response = requests.get(url, headers=st.session_state.api.get_headers())
        st.session_state.api_calls.append(f"Response: {response.status_code}")
        
        if response.status_code != 200:
            st.session_state.api_calls.append(f"Error: {response.text}")
            return []
            
        root = ET.fromstring(response.text)
        dataflows = []
        
        ns = {
            'structure': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
            'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
        }
        
        for dataflow in root.findall('.//structure:Dataflow', ns):
            dataflow_id = dataflow.get('id')
            name = dataflow.find('.//common:Name', ns)
            description = dataflow.find('.//common:Description', ns)
            
            if name is not None:
                dataflows.append({
                    'id': dataflow_id,
                    'name': name.text,
                    'description': description.text if description is not None else ''
                })
        
        return dataflows
    except Exception as e:
        st.session_state.api_calls.append(f"Exception: {str(e)}")
        return []

def search_dataflows(search_term: str, dataflows: list) -> list:
    """Recherche dans les dataflows localement"""
    search_term = normalize_search_term(search_term)
    matching_dataflows = []
    
    for dataflow in dataflows:
        if (search_term in normalize_search_term(dataflow['id']) or
            search_term in normalize_search_term(dataflow['name']) or
            search_term in normalize_search_term(dataflow['description'])):
            matching_dataflows.append(dataflow)
    
    return matching_dataflows

def get_series_from_dataflow(dataflow_id: str) -> list:
    """Récupère les séries d'un dataflow"""
    try:
        url = f"https://api.insee.fr/series/BDM/V1/data/{dataflow_id}/all"
        
        # Log de l'appel API
        st.session_state.api_calls.append(f"GET {url}")
        
        response = requests.get(url, headers=st.session_state.api.get_headers())
        st.session_state.api_calls.append(f"Response: {response.status_code}")
        
        if response.status_code != 200:
            st.session_state.api_calls.append(f"Error: {response.text}")
            return []
            
        root = ET.fromstring(response.text)
        series_list = []
        
        for series in root.findall('.//Series'):
            series_list.append({
                'IdBank': series.get('IDBANK'),
                'Titre': series.get('TITLE_FR'),
                'Unité': series.get('UNIT_MEASURE'),
                'Fréquence': series.get('FREQ'),
                'Dernière mise à jour': series.get('LAST_UPDATE')
            })
        
        return series_list
    except Exception as e:
        st.session_state.api_calls.append(f"Exception: {str(e)}")
        return []

# Interface de recherche
st.subheader("🔍 Étape 1 : Rechercher un thème")

# Chargement initial des dataflows si nécessaire
if st.session_state.all_dataflows is None:
    with st.spinner("Chargement des thèmes disponibles..."):
        st.session_state.all_dataflows = get_all_dataflows()
        if not st.session_state.all_dataflows:
            st.error("❌ Erreur lors du chargement des thèmes")
            st.stop()

# Recherche par texte
search_term = st.text_input("Entrez un terme de recherche (ex: construction, population)")

# Bouton de recherche
search_clicked = st.button("🔎 Lancer la recherche")

# Lancement de la recherche
if search_clicked or search_term:
    if search_term:
        matching_dataflows = search_dataflows(search_term, st.session_state.all_dataflows)
        
        if matching_dataflows:
            st.success(f"✅ {len(matching_dataflows)} thèmes trouvés")
            
            # Affichage des dataflows trouvés dans un tableau
            df_dataflows = pd.DataFrame([
                {
                    'ID': df['id'],
                    'Nom': df['name'],
                    'Description': df['description']
                }
                for df in matching_dataflows
            ])
            
            st.dataframe(
                df_dataflows,
                hide_index=True,
                column_config={
                    "ID": st.column_config.TextColumn("ID", width="medium"),
                    "Nom": st.column_config.TextColumn("Nom", width="large"),
                    "Description": st.column_config.TextColumn("Description", width="large")
                }
            )
            
            # Sélection d'un dataflow
            selected = st.selectbox(
                "👉 Étape 2 : Sélectionner un thème pour voir ses séries",
                options=[f"{df['name']} ({df['id']})" for df in matching_dataflows],
                format_func=lambda x: x.split('(')[0].strip()
            )
            
            if selected:
                dataflow_id = selected.split('(')[-1].strip(')')
                if dataflow_id != st.session_state.selected_dataflow:
                    st.session_state.selected_dataflow = dataflow_id
                    st.session_state.search_results = None
                    st.rerun()
        else:
            st.warning("Aucun thème trouvé")
    else:
        st.warning("Veuillez entrer un terme de recherche")
else:
    st.info("👆 Commencez par entrer un terme de recherche")

# Si un dataflow est sélectionné, afficher ses séries
if st.session_state.selected_dataflow:
    st.subheader(f"📊 Séries du thème : {st.session_state.selected_dataflow}")
    
    if st.session_state.search_results is None:
        with st.spinner("Chargement des séries..."):
            series_list = get_series_from_dataflow(st.session_state.selected_dataflow)
            if series_list:
                st.session_state.search_results = pd.DataFrame(series_list)
                st.success(f"✅ {len(series_list)} séries trouvées")
            else:
                st.warning("Aucune série trouvée dans ce thème")
    
    if st.session_state.search_results is not None:
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            freq_filter = st.multiselect(
                "📅 Filtrer par fréquence",
                options=sorted(st.session_state.search_results['Fréquence'].unique())
            )
        
        # Application des filtres
        filtered_df = st.session_state.search_results.copy()
        if freq_filter:
            filtered_df = filtered_df[filtered_df['Fréquence'].isin(freq_filter)]
        
        # Affichage du tableau
        st.dataframe(
            filtered_df,
            hide_index=True,
            column_config={
                "IdBank": st.column_config.TextColumn("IdBank", width="medium"),
                "Titre": st.column_config.TextColumn("Titre", width="large"),
                "Unité": st.column_config.TextColumn("Unité", width="medium"),
                "Fréquence": st.column_config.TextColumn("Fréquence", width="small"),
                "Dernière mise à jour": st.column_config.DateColumn("Dernière mise à jour", width="medium")
            }
        )

# Footer avec informations
st.markdown("---")
st.markdown("""
💡 **Comment utiliser cet explorateur :**
1. Rechercher un thème :
   - Entrez un terme de recherche (ex: construction, population)
   - Les thèmes correspondants s'affichent
2. Explorer les séries :
   - Sélectionnez un thème dans la liste
   - Parcourez les séries disponibles
   - Utilisez les filtres pour affiner les résultats
3. Utiliser une série :
   - Copiez son IdBank
   - Utilisez-le dans la page de visualisation
""")
st.markdown("*Données fournies par l'INSEE via l'API BDM*")