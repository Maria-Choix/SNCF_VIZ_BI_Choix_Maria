# Le réseau ferré national

Application Streamlit pour explorer le réseau ferré français : voies, longueurs et temps de parcours.

Auteure : Maria Choix("https://github.com/mariachoice")


## Axes d'étude

- Comparer les longueurs du réseau et les types de voies (VPL, VPA, VS)
- Suivre la performance des trains par relation, au fil des années
- Mesurer l'efficacité d'un trajet : temps de parcours rapporté à la distance à vol d'oiseau




## Onglets/graphes

- **Contexte** : problématique, public et questions d'analyse
- **Tableau de bord, KPIs** :longueur et nombre de tronçons par type de voie, 10 lignes les plus longues
- **Carte** : carte interactive filtrable, répartition des voies, statistiques
- **Horaires** : évolution d'une relation, évolution des temps de parcours dans le temps, 10 plus rapides, ratio rapidité / distance, 10 plus longues, distribution et temps moyen par année. Chaque graphe est commenté (causes/conséquences/hypothèses)
**Les 10 relations avec le meilleur ratio rapidité / distance (à vol d'oiseau)**
--> Lollipop Chart : Remplacement des points basiques par des icones de trains
- **Insights** : Implications et recommandations (pistes d'atttention)
- **Documentation** : source, méthodologie, variables, définitions


## Lancement

```bash
pip install streamlit pandas plotly pydeck pillow watchdog
streamlit run app.py
```

Les deux fichiers CSV (réseau et temps de parcours) doivent être dans le dossier de `app.py`.

## Source

SNCF Réseau, fichier de formes des voies du Réseau Ferré National. (data.gouv.fr)

---

### Usage de l'IA
- Génération des icônes de trains (train_grenat.png et train_rose.png)
- Génération de la bibliothèque de couleurs (app.py.couleurs_hex)