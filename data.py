# ============================================================
# DOCUMENTATION
# ============================================================

TITRE = "Le réseau ferré national"

DESCRIPTION = """
Cette application permet d'explorer le réseau ferré national
à travers une carte interactive, des statistiques et des graphiques.

Les données représentent les voies du Réseau Ferré National (RFN).
"""

SOURCE = """
1 : SNCF Réseau — Fichier de formes des voies du Réseau Ferré National. (data.gouv.fr)  
2 : SNCF Réseau - Meilleurs temps de parcours sur le réseau ferré national (1920‑2020). (data.gouv.fr)
"""

METHODOLOGIE = """
Les données sont issues du jeu de données Open Data de SNCF Réseau.

Chaque enregistrement correspond à une portion de voie ferrée.

La longueur affichée dans l'application est calculée
à partir de la géométrie géographique du tronçon.
"""

VARIABLES = {
    "ligne": "Code du tronçon de ligne ferroviaire.",
    "type_voie": "Type de voie : VPL, VPA ou VS.",
    "geo_shape": "Géométrie géographique de la portion de voie.",
    "code_ligne": "Identifiant SNCF Réseau de la ligne.",
    "idgaia": "Identifiant technique de la voie.",
    "rg_troncon": "Numéro d'ordre du tronçon sur la ligne.",
    "nom_voie": "Code identifiant une voie.",
    "code_voie": "Code de localisation de la voie.",
    "pk_debut_r": "Repère kilométrique du début du tronçon.",
    "pk_fin_r": "Repère kilométrique de fin du tronçon.",
}

DEF = {
    "VPL": "Voie principale à écartement standard.\n",
    "VPA": "Voie principale à écartement particulier.\n",
    "VS": "Voie secondaire.\n",
    "Tronçon" : "Portion d'une voie ferrée délimité par des points de jonctions tels qu'un aiguillage, une bifurcation, une gare ou une intersection.\n",
    "PK (Point Kilométrique)" : "Repère indiquant la distance en kilomètres depuis un point de référence sur la ligne. (Différent de l'abscisse curviligne qui est la distance le long de la voie."


}
    
    