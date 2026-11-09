# Le réseau ferré national

Application Streamlit pour explorer le réseau ferré français : voies, longueurs et temps de parcours.

Auteure : @user.name("https://github.com/mariachoice")

!!!!A AJOUTER
- insights faire
- dataset de contexte, manque de performance


## Axes d'étude

- Comparer les longueurs du réseau et les types de voies (VPL, VPA, VS)
- Suivre la performance des trains par relation, au fil des années
- Mesurer l'efficacité d'un trajet : temps de parcours rapporté à la distance à vol d'oiseau




## Onglets/graphes

- **Tableau de bord** : longueur et nombre de tronçons par type de voie, 10 lignes les plus longues
- **Carte** : carte interactive filtrable, répartition des voies, statistiques
- **Horaires** : évolution d'une relation, 10 plus rapides, ratio rapidité / distance, 10 plus longues, distribution et temps moyen par année. 
**Les 10 relations avec le meilleur ratio rapidité / distance (à vol d'oiseau)**
--> Lollipop Chart : Remplacement des points basiques par des icones de trains
- **Documentation** : source, méthodologie, variables, définitions


## Lancement

```bash
pip install streamlit pandas plotly pydeck pillow watchdog
streamlit run app.py
```

Les deux fichiers CSV (réseau et temps de parcours) doivent être dans le dossier de `app.py`.

## Source

SNCF Réseau, fichier de formes des voies du Réseau Ferré National. (data.gouv.fr)