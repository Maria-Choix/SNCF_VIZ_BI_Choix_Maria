import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json
import math

from data import TITRE, DESCRIPTION, SOURCE, METHODOLOGIE, VARIABLES, DEF

from PIL import Image

from onglets import contexte, dashboard, carte, horaires, insights, documentation

#### image scatter train icone
@st.cache_resource
def icone_train_rose():
    return Image.open("train_rose.png").convert("RGBA")
def icone_train_grenat():
    return Image.open("train_grenat.png").convert("RGBA")
###

LIBELLES_TYPES = {
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


couleurs_hex = {
    # Neutres
    "blanc": "#FFFFFF",
    "ivoire": "#F7F5F0",
    "gris_clair": "#E5E7EB",
    "gris": "#9CA3AF",
    "gris_fonce": "#4B5563",
    "ardoise": "#1F2937",
    "noir": "#0F172A",

    # Bleus
    "ciel": "#7DD3FC",
    "azur": "#38BDF8",
    "bleu": "#3B82F6",
    "bleu_roi": "#2563EB",
    "indigo": "#4F46E5",
    "marine": "#1E3A8A",
    "nuit": "#0D1B2A",

    # Verts
    "menthe": "#6EE7B7",
    "emeraude": "#10B981",
    "vert": "#22A06B",
    "sapin": "#166534",
    "olive": "#84A98C",
    "sauge": "#A3B18A",

    # Teals
    "turquoise": "#2DD4BF",
    "lagune": "#0E7C86",
    "canard": "#0F766E",

    # Jaunes / oranges
    "citron": "#FDE047",
    "soleil": "#FACC15",
    "ambre": "#F59E0B",
    "orange": "#FB923C",
    "corail": "#FF7A59",
    "abricot": "#FDBA74",

    # Rouges / roses
    "rouge": "#EF4444",
    "grenat": "#9F1239",
    "framboise": "#D6336C",
    "rose": "#F472B6",
    "rose_poudre": "#FBCFE8",

    # Violets
    "lavande": "#C4B5FD",
    "violet": "#8B5CF6",
    "prune": "#6B21A8",
    "aubergine": "#3B0764",
    "lilas_fonce" : "#332736",
    "lilas_doux" : "#49284D",

    # Palette de la maquette (interface sombre + cartes pastel)
    "maq_fond": "#17171B",
    "maq_surface": "#222227",
    "maq_surface_2": "#2C2C33",
    "maq_bordure": "#34343C",
    "maq_texte": "#FFFFFF",
    "maq_texte_doux": "#9B9BA5",
    "maq_vert": "#9BBF8B",
    "maq_jaune": "#F9D78C",
    "maq_rose": "#F2A7C3",
    "maq_violet": "#7468D4",
    "maq_vert_clair": "#BBD7AE",
    "maq_jaune_clair": "#FBE6B5",
    "maq_rose_clair": "#F8CBDB",
    "maq_violet_clair": "#A59CE8",

    # Statuts
    "succes": "#2E9E6B",
    "alerte": "#E0A100",
    "erreur": "#D64550",
    "info": "#3B82C4",
}

  

st.set_page_config(page_title="Le réseau ferré national", page_icon="🚆", layout="wide")


# --------------------------------------------------------------------------- #
# Couleurs
# --------------------------------------------------------------------------- #

FOND = couleurs_hex["maq_fond"]
SURFACE = couleurs_hex["maq_surface"]
SURFACE_2 = couleurs_hex["maq_surface_2"]
TEXTE = couleurs_hex["maq_texte"]
TEXTE_DOUX = couleurs_hex["maq_texte_doux"]
BORDURE = couleurs_hex["maq_bordure"]
PRIMAIRE = couleurs_hex["maq_violet"]
ACCENT = couleurs_hex["maq_jaune"]
VERT = couleurs_hex["maq_vert"]
JAUNE = couleurs_hex["maq_jaune"]
ROSE = couleurs_hex["maq_rose"]
VIOLET = couleurs_hex["maq_violet"]
GRENAT = couleurs_hex["grenat"]

# Palette utilisée pour les types de voie (et comme séquence par défaut des graphiques)
PALETTE_TYPES = [
    couleurs_hex[nom]
    for nom in ["maq_vert", "maq_jaune", "maq_rose", "maq_violet",
                "maq_vert_clair", "maq_jaune_clair", "maq_rose_clair", "maq_violet_clair"]
]

# Thème Plotly commun à tous les graphiques
pio.templates["rail"] = go.layout.Template(
    layout=go.Layout(
        colorway=PALETTE_TYPES,
        font=dict(color=TEXTE),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=BORDURE, zerolinecolor=BORDURE, linecolor=BORDURE),
        yaxis=dict(gridcolor=BORDURE, zerolinecolor=BORDURE, linecolor=BORDURE),
        legend=dict(font=dict(color=TEXTE)),
        hoverlabel=dict(bgcolor=SURFACE_2, font_color=TEXTE, bordercolor=BORDURE),
    )
)
pio.templates.default = "plotly_dark+rail"

# Thème de l'interface Streamlit
st.markdown(
    f"""
<style>
.stApp {{ background: {FOND}; color: {TEXTE}; }}
[data-testid="stHeader"] {{ background: transparent; }}
h1, h2, h3, h4, h5, p, label, li {{ color: {TEXTE}; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: {TEXTE_DOUX}; }}

[data-testid="stSidebar"] {{
  background: {SURFACE};
  border-right: 1px solid {BORDURE};
}}

/* Cartes de métriques : pastilles colorées façon maquette */
[data-testid="stMetric"] {{
  background: {SURFACE};
  border: 1px solid {BORDURE};
  border-left: 4px solid {PRIMAIRE};
  border-radius: 20px;
  padding: 14px 18px;
}}
[data-testid="stMetricLabel"] p {{ color: {TEXTE_DOUX}; }}
[data-testid="stMetricValue"] {{ color: {TEXTE}; }}
[data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {{ border-left-color: {VERT}; }}
[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {{ border-left-color: {JAUNE}; }}
[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {{ border-left-color: {ROSE}; }}
[data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {{ border-left-color: {VIOLET}; }}

/* Onglets */
[data-baseweb="tab"] {{ color: {TEXTE_DOUX}; }}
[data-baseweb="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] p {{ color: {JAUNE}; }}
[data-baseweb="tab-highlight"] {{ background: {JAUNE}; }}
[data-baseweb="tab-border"] {{ background: {BORDURE}; }}

/* Expander, champs, tableaux */
[data-testid="stExpander"] {{
  background: {SURFACE};
  border: 1px solid {BORDURE};
  border-radius: 20px;
}}
[data-baseweb="select"] > div, [data-baseweb="input"] > div {{
  background: {SURFACE};
  border: 1px solid {BORDURE};
  border-radius: 14px;
  color: {TEXTE};
}}
[data-baseweb="popover"] ul {{ background: {SURFACE_2}; }}
[data-baseweb="tag"] {{ background: {PRIMAIRE}; border-radius: 10px; }}
[data-baseweb="tag"] span {{ color: {TEXTE}; }}
[data-testid="stDataFrame"] {{ border: 1px solid {BORDURE}; border-radius: 16px; overflow: hidden; }}
[data-testid="stAlert"] {{ background: {JAUNE}; border-radius: 16px; }}
[data-testid="stAlert"] p {{ color: {FOND}; }}
.stButton > button {{
  background: {VERT}; color: {FOND};
  border: none; border-radius: 14px;
}}
hr {{ border-color: {BORDURE}; }}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Données : chargement, nettoyage et fonctions
# --------------------------------------------------------------------------- #

COL_DISTANCE = "distance"


@st.cache_data
def charger_donnees():
    fichier1 = "fichier-de-formes-des-voies-du-reseau-ferre-national.csv"
    try:
        df = pd.read_csv(fichier1, sep=";", quotechar='"', encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(fichier1, sep=",", quotechar='"', encoding="utf-8-sig")

    df.columns = df.columns.str.strip().str.lower()

    fichier2 = "meilleurs-temps-des-parcours-des-trains.csv"
    try:
        df2 = pd.read_csv(fichier2, sep=";", quotechar='"', encoding="utf-8-sig")
    except Exception:
        df2 = pd.read_csv(fichier2, sep=",", quotechar='"', encoding="utf-8-sig")

    df2.columns = df2.columns.str.strip().str.lower()
    return df, df2


def clean_reseau(data):
    resultat = data.copy()
    resultat = resultat.dropna(subset=["ligne", "type_voie", "geo shape"])
    resultat["type_voie"] = resultat["type_voie"].astype(str).str.strip().str.upper()
    resultat["ligne"] = resultat["ligne"].astype(str).str.strip()
    return resultat


def clean_horaires(data):
    resultat = data.copy()
    resultat = resultat.dropna(subset=["relations", "année", "temps estimé en minutes"])
    resultat["relations"] = resultat["relations"].astype(str).str.strip().str.upper()
    resultat["année"] = pd.to_numeric(resultat["année"], errors="coerce")
    resultat["temps estimé en minutes"] = pd.to_numeric(resultat["temps estimé en minutes"], errors="coerce")
    resultat = resultat.dropna(subset=["année", "temps estimé en minutes"])
    resultat["année"] = resultat["année"].astype(int)
    return resultat


def distance_km(point1, point2):
    lon1, lat1 = point1
    lon2, lat2 = point2
    rayon = 6371.0
    lat1, lat2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return rayon * c


def extraire_paths(geo_shape):
    try:
        geo = geo_shape if isinstance(geo_shape, dict) else json.loads(str(geo_shape))
        geometrie = geo.get("type")
        coordinates = geo.get("coordinates")
        if not coordinates:
            return []
        if geometrie == "LineString":
            return [coordinates]
        if geometrie == "MultiLineString":
            return coordinates
        return []
    except Exception:
        return []


def longueur_geometry(geo_shape):
    paths = extraire_paths(geo_shape)
    longueur = 0
    for path in paths:
        if len(path) < 2:
            continue
        for i in range(len(path) - 1):
            try:
                longueur += distance_km(path[i], path[i + 1])
            except Exception:
                pass
    return longueur


@st.cache_data
def calculer_longueurs(data):
    resultat = data.copy()
    resultat["longueur_km"] = resultat["geo shape"].apply(longueur_geometry)
    return resultat


def fr(nombre):
    return f"{nombre:,.0f}".replace(",", " ")


def fr_decimal(nombre):
    return f"{nombre:,.1f}".replace(",", " ")


def minutes_vers_heure(minutes):
    minutes = int(round(minutes))
    heures = minutes // 60
    minutes_restantes = minutes % 60
    if heures > 0:
        return f"{heures} h {minutes_restantes:02d}"
    return f"{minutes} min"


df, df2 = charger_donnees()
df = clean_reseau(df)
nb_brut_horaires = len(df2)
df2 = clean_horaires(df2)
df = calculer_longueurs(df)

# Une couleur par type de voie, attribuée automatiquement depuis la palette
COULEURS_HEX = {
    code: PALETTE_TYPES[i % len(PALETTE_TYPES)]
    for i, code in enumerate(sorted(df["type_voie"].unique()))
}



# --------------------------------------------------------------------------- #
# BODY 
# --------------------------------------------------------------------------- #


with st.sidebar:
    st.image("emoticon.png", width=120)
    st.markdown("##  Le réseau ferré national")
    st.markdown("---")

    st.markdown("### À propos")
    st.write("Cette application permet d'explorer le réseau ferré national à travers des statistiques, des graphiques et une carte interactive.")

    st.markdown("### Informations")
    st.write("**Source :** SNCF Réseau")
    st.write("**Projet :** 2026")
    st.write("**Réalisé par :** Maria Choix")

    st.markdown("### Contenu")
    st.write("Tableau de bord")
    st.write("Carte")
    st.write("Horaires")
    st.write("Documentation")

    st.markdown("---")
    st.caption("© 2026 Maria Choix")


st.title("Le réseau ferré national")
st.write("Explorez les infrastructures ferroviaires françaises à travers les données de SNCF Réseau.")


tab_contexte, tab_dashboard, tab_carte, tab_horaires, tab_ins, tab_doc = st.tabs([
    "Contexte",
    "Tableau de bord",
    "Carte",
    "Horaires",
    "Insights",
    "Documentation"
])

with tab_contexte:
    contexte.afficher()

with tab_dashboard:
    dashboard.afficher(df, fr, fr_decimal, COULEURS_HEX, LIBELLES_TYPES)


with tab_carte:
    carte.afficher(df, extraire_paths, COULEURS_HEX, couleurs_hex, LIBELLES_TYPES)


with tab_horaires:
    horaires.afficher(df2, fr, minutes_vers_heure, COL_DISTANCE, ACCENT, ROSE, GRENAT, icone_train_rose, icone_train_grenat)

with tab_ins:
    insights.afficher(df, df2, COL_DISTANCE, nb_brut_horaires, ACCENT)

with tab_doc:
    documentation.afficher()
