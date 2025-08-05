import requests
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Union, Optional

class InseeBdmAPI:
    """
    Classe pour interagir avec l'API BDM (Banque de Données Macroéconomiques) de l'INSEE
    """
    def __init__(self, consumer_key: str = None, consumer_secret: str = None):
        self.base_url = "https://api.insee.fr/series/BDM"
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = None

    def get_token(self) -> bool:
        """
        Obtient un token d'accès OAuth2
        """
        if not self.consumer_key or not self.consumer_secret:
            print("Clés d'API manquantes")
            return False

        auth_url = "https://api.insee.fr/token"
        auth = (self.consumer_key, self.consumer_secret)
        headers = {'Accept': 'application/json'}
        data = {'grant_type': 'client_credentials'}

        try:
            print(f"Tentative d'authentification...")
            response = requests.post(auth_url, auth=auth, headers=headers, data=data)
            
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                print("Authentification réussie")
                return True
            else:
                print(f"Échec de l'authentification : {response.status_code}")
                print(f"Réponse : {response.text}")
        except Exception as e:
            print(f"Erreur lors de l'authentification : {str(e)}")
        return False

    def get_headers(self, accept_type='application/xml') -> Dict:
        """
        Prépare les headers pour les requêtes API
        """
        headers = {
            'Accept': accept_type,
            'Content-Type': accept_type
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def search_series(self, query: str) -> List[Dict]:
        """
        Recherche des séries dans l'annuaire BDM
        
        Args:
            query (str): Terme de recherche
            
        Returns:
            list: Liste des séries trouvées
        """
        # L'API BDM est en libre accès, pas besoin d'authentification
        # if not self.token and not self.get_token():
        #     return {"error": "Authentification requise"}

        # Utilisation de l'API de recherche
        url = f"{self.base_url}/data/SERIES_BDM"
        headers = self.get_headers()
        
        try:
            # D'abord, récupérons toutes les séries disponibles
            response = requests.get(url, headers=headers)
            print(f"URL de recherche : {response.url}")
            print(f"Status code : {response.status_code}")
            
            if response.status_code == 200:
                # Parse le XML
                root = ET.fromstring(response.text)
                series_list = []
                query_lower = query.lower()
                
                # Recherche dans les séries
                for series in root.findall('.//Series'):
                    title_fr = series.get('TITLE_FR', '').lower()
                    idbank = series.get('IDBANK', '')
                    
                    # Si le terme de recherche est dans le titre ou l'idbank
                    if query_lower in title_fr or query_lower in idbank.lower():
                        serie_info = {
                            'idbank': idbank,
                            'title_fr': series.get('TITLE_FR'),
                            'title_en': series.get('TITLE_EN'),
                            'unit': series.get('UNIT_MEASURE'),
                            'frequency': series.get('FREQ'),
                            'last_update': series.get('LAST_UPDATE')
                        }
                        series_list.append(serie_info)
                
                print(f"Nombre de séries trouvées : {len(series_list)}")
                return series_list
            else:
                print(f"Erreur de recherche : {response.text}")
                return {"error": f"Erreur {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"Exception lors de la recherche : {str(e)}")
            return {"error": f"Erreur lors de la recherche : {str(e)}"}

    def format_idbank(self, idbank: str) -> str:
        """
        Formate un idBank en ajoutant les zéros manquants au début
        """
        idbank = ''.join(filter(str.isdigit, idbank))
        return idbank.zfill(9)

    def parse_series_xml(self, xml_data: str) -> Dict:
        """
        Parse les données XML de l'API en dictionnaire
        """
        try:
            # Parse le XML
            root = ET.fromstring(xml_data)
            
            # Recherche de la série dans le XML
            series_list = root.findall('.//Series')
            if not series_list:
                print("Aucune série trouvée dans le XML")
                print(f"Contenu XML reçu : {xml_data[:500]}...")
                return {"error": "Aucune série trouvée dans les données"}
            
            series = series_list[0]
            print(f"Série trouvée avec ID : {series.get('IDBANK')}")
            
            # Récupère les métadonnées de la série
            metadata = {
                'IDBANK': series.get('IDBANK'),
                'TITLE_FR': series.get('TITLE_FR'),
                'TITLE_EN': series.get('TITLE_EN'),
                'LAST_UPDATE': series.get('LAST_UPDATE'),
                'UNIT_MEASURE': series.get('UNIT_MEASURE')
            }
            
            # Récupère les observations
            observations = []
            for obs in series.findall('.//Obs'):
                observation = {
                    'date': obs.get('TIME_PERIOD'),
                    'valeur': float(obs.get('OBS_VALUE')),
                    'statut': obs.get('OBS_STATUS'),
                    'qualite': obs.get('OBS_QUAL')
                }
                observations.append(observation)
            
            print(f"Nombre d'observations trouvées : {len(observations)}")
            
            # Tri des observations par date
            observations.sort(key=lambda x: x['date'])
            
            return {
                'metadata': metadata,
                'observations': observations
            }
            
        except ET.ParseError as e:
            print(f"Erreur de parsing XML : {str(e)}")
            print(f"Données XML reçues : {xml_data[:200]}...")
            return {"error": f"Erreur lors du parsing XML : {str(e)}"}
        except Exception as e:
            print(f"Erreur inattendue : {str(e)}")
            return {"error": f"Erreur inattendue : {str(e)}"}

    def get_series_by_idbank(self, idbanks: Union[str, List[str]], 
                           first_nth_observations: Optional[int] = None,
                           last_nth_observations: Optional[int] = None,
                           start_period: Optional[str] = None,
                           end_period: Optional[str] = None) -> Dict:
        """
        Récupère les données des séries par leurs identifiants idBank
        """
        # L'API BDM est en libre accès, pas besoin d'authentification
        # if not self.token and not self.get_token():
        #     return {"error": "Authentification requise"}

        # Conversion en liste si nécessaire
        if isinstance(idbanks, str):
            idbanks = [idbanks]
            
        # Formatage des idBanks
        idbanks = [self.format_idbank(idbank) for idbank in idbanks]
        
        # Vérification de la limite
        if len(idbanks) > 400:
            return {"error": "Le nombre maximum d'idBank est limité à 400"}
            
        # Construction des paramètres
        params = {}
        if first_nth_observations:
            params['firstNObservations'] = first_nth_observations
        if last_nth_observations:
            params['lastNObservations'] = last_nth_observations
        if start_period:
            params['startPeriod'] = start_period
        if end_period:
            params['endPeriod'] = end_period
            
        # Construction de l'URL selon la documentation
        idbanks_path = '+'.join(idbanks)
        url = f"{self.base_url}/data/SERIES_BDM/{idbanks_path}"
        
        print(f"URL de la requête : {url}")
        print(f"Paramètres : {params}")
        
        # Appel de l'API
        response = requests.get(url, params=params, headers=self.get_headers())
        
        print(f"Status code : {response.status_code}")
        if response.status_code != 200:
            print(f"Réponse d'erreur : {response.text}")
            
        if response.status_code == 200:
            return self.parse_series_xml(response.text)
        return {"error": f"Erreur {response.status_code}: {response.text}"}