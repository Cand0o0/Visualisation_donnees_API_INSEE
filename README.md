# Application de Visualisation des Données INSEE

Cette application Streamlit permet de visualiser et explorer les données de l'INSEE via l'API BDM (Banque de Données Macroéconomiques).

## 🚀 Fonctionnalités

### 📊 Page principale - Visualisation des séries
- **Authentification globale** : Système d'authentification centralisé pour toutes les pages
- **Gestion des séries** : Ajout, suppression et recherche de séries temporelles
- **Visualisation interactive** : Graphiques Plotly avec zoom, pan et hover
- **Indicateurs de chargement** : Feedback visuel pendant les appels API
- **Sauvegarde automatique** : Les séries ajoutées sont sauvegardées localement

### 🔍 Page Explorateur - Découverte des données
- **Recherche par thème** : Exploration des dataflows disponibles
- **Filtrage par fréquence** : Affichage des séries selon leur périodicité
- **Détails des appels API** : Debug en temps réel des requêtes
- **Interface intuitive** : Navigation simple et efficace

## 🔐 Authentification

L'application utilise un système d'authentification global :

1. **Configuration** : Les identifiants sont stockés dans `.streamlit/secrets.toml`
2. **Session partagée** : Une fois connecté, l'accès est valide sur toutes les pages
3. **Déconnexion** : Bouton de déconnexion disponible dans la sidebar
4. **Sécurité** : Les identifiants ne sont jamais exposés dans le code

### Configuration des identifiants

Le fichier `.streamlit/secrets.toml` est déjà configuré avec :

```toml
[authentication]
username = "echaf"
password = "balea10bateau*"
```

## 📦 Installation

1. **Cloner le repository**
```bash
git clone <url_du_repo>
cd echa
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Authentification configurée**
```bash
# Les identifiants sont déjà configurés dans .streamlit/secrets.toml
```

4. **Lancer l'application**
```bash
streamlit run insee_web_app.py
```

## 🛠️ Structure du projet

```
echa/
├── insee_web_app.py          # Application principale
├── pages/
│   └── explorer_series.py    # Page explorateur
├── config.py                 # Configuration globale
├── insee_bdm_api.py          # Interface API INSEE
├── .streamlit/
│   └── secrets.toml          # Identifiants (à créer)
├── saved_series.json         # Séries sauvegardées
└── requirements.txt          # Dépendances
```

## 🔧 Améliorations récentes

### Authentification globale
- ✅ Authentification centralisée dans `config.py`
- ✅ Session partagée entre toutes les pages
- ✅ Bouton de déconnexion dans la sidebar
- ✅ Gestion sécurisée des identifiants

### Expérience utilisateur
- ✅ Indicateurs de chargement pour tous les appels API
- ✅ Feedback visuel pendant les opérations
- ✅ Gestion d'erreurs améliorée
- ✅ Interface plus réactive

### Performance
- ✅ Cache des dataflows pour éviter les rechargements
- ✅ Optimisation des appels API
- ✅ Gestion d'état centralisée

### Persistance des données
- ✅ Sauvegarde automatique des séries dans `saved_series.json`
- ✅ Persistance entre les sessions (redémarrage de l'application)
- ✅ Chargement automatique au démarrage
- ✅ Possibilité de réinitialiser les séries

## 📊 Utilisation

### 1. Connexion
- Lancez l'application
- Entrez vos identifiants dans le formulaire d'authentification
- Une fois connecté, vous avez accès à toutes les fonctionnalités

### 2. Visualisation des séries
- Sélectionnez une série dans la liste déroulante
- Ajustez la période d'analyse avec le slider
- Le graphique se met à jour automatiquement

### 3. Gestion des séries
- **Ajouter** : Saisissez un nom et un IdBank, ou utilisez la recherche
- **Rechercher** : Trouvez de nouvelles séries par mot-clé
- **Supprimer** : Cochez les séries à supprimer

### 4. Exploration des données
- Naviguez vers la page "Explorateur des séries"
- Recherchez un thème (ex: construction, population)
- Sélectionnez un thème pour voir ses séries
- Utilisez les filtres pour affiner les résultats

### 5. Sauvegarde et persistance
- Les séries ajoutées sont automatiquement sauvegardées
- Elles persistent entre les sessions (redémarrage de l'application)
- Consultez le nombre de séries sauvegardées dans la sidebar
- Utilisez le bouton "Réinitialiser" pour revenir aux séries par défaut

## 🔍 Debug et monitoring

La page explorateur inclut une zone de debug qui affiche :
- Les URLs des appels API
- Les codes de réponse HTTP
- Les erreurs éventuelles
- Les exceptions levées

## 📝 Notes techniques

- **API INSEE BDM** : Accès libre, pas de clé API requise
- **Session Streamlit** : État partagé entre les pages
- **Sauvegarde JSON** : Persistance des séries favorites
- **Responsive design** : Interface adaptée à tous les écrans

## 🐛 Dépannage

### Problème d'authentification
- Vérifiez que le fichier `.streamlit/secrets.toml` existe
- Assurez-vous que les identifiants sont corrects
- Redémarrez l'application si nécessaire

### Erreurs API
- Consultez la zone de debug dans l'explorateur
- Vérifiez votre connexion internet
- Les appels API peuvent prendre du temps, soyez patient

### Problèmes d'affichage
- Actualisez la page si les données ne se chargent pas
- Vérifiez que toutes les dépendances sont installées
- Consultez les logs de Streamlit

## 📞 Support

Pour toute question ou problème :
1. Consultez la zone de debug
2. Vérifiez la configuration
3. Redémarrez l'application
4. Contactez l'équipe de développement

---

*Données fournies par l'INSEE via l'API BDM* 