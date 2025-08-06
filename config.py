import streamlit as st
import os

def init_session_state():
    """Initialise les variables de session globales"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'api' not in st.session_state:
        st.session_state.api = None
    
    if 'series_options' not in st.session_state:
        st.session_state.series_options = {}
    
    if 'all_dataflows' not in st.session_state:
        st.session_state.all_dataflows = None
    
    if 'selected_dataflow' not in st.session_state:
        st.session_state.selected_dataflow = None
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    
    if 'api_calls' not in st.session_state:
        st.session_state.api_calls = []

def check_global_authentication():
    """Vérifie l'authentification de l'utilisateur de manière globale"""
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

def logout():
    """Déconnecte l'utilisateur"""
    st.session_state.authenticated = False
    st.session_state.api = None
    st.session_state.series_options = {}
    st.session_state.all_dataflows = None
    st.session_state.selected_dataflow = None
    st.session_state.search_results = None
    st.session_state.api_calls = []
    st.rerun()

def show_logout_button():
    """Affiche le bouton de déconnexion dans la sidebar"""
    if st.session_state.authenticated:
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Se déconnecter"):
            logout()

def get_default_series():
    """Retourne les séries par défaut"""
    return {
        "Population française": "001641607",
        "Indice des prix à la consommation": "001769682",
        "Taux de chômage": "001688526"
    } 