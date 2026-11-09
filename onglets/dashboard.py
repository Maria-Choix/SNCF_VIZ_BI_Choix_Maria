import streamlit as st
import plotly.express as px


def afficher(df, fr, fr_decimal, COULEURS_HEX, LIBELLES_TYPES):
    st.subheader("Tableau de bord : KPIs")
    st.caption("Vue générale du réseau ferré national.")

    nb_troncons = len(df)
    nb_lignes = df["ligne"].nunique()
    longueur_totale = df["longueur_km"].sum()
    nb_types = df["type_voie"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tronçons", fr(nb_troncons))
    col2.metric("Lignes", fr(nb_lignes))
    col3.metric("Longueur estimée", f"{fr_decimal(longueur_totale)} km")
    col4.metric("Types de voie", fr(nb_types))

    st.divider()

    st.markdown("#### Longueur du réseau par type de voie")

    LIBELLES_VOIES = {
    "VPL": "Voie principale de ligne",
    "VPA": "Voie principale autre",
    "VS": "Voie de service" }

    par_type = df.groupby("type_voie")["longueur_km"].sum().sort_values(ascending=False).reset_index()
    par_type["nom"] = par_type["type_voie"].map(LIBELLES_VOIES)

    couleurs_noms = {LIBELLES_TYPES.get(code, code): couleur for code, couleur in COULEURS_HEX.items()}

    fig = px.bar(
        par_type,
        x="longueur_km",
        y="nom",
        orientation="h",
        color="nom",
        color_discrete_map=couleurs_noms,
        labels={"longueur_km": "Longueur (km)", "nom": "Type de voie"}
    )
    fig.update_layout(showlegend=False, height=400, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown("#### Nombre de tronçons par type de voie")

    nb_par_type = df["type_voie"].value_counts().reset_index()
    nb_par_type.columns = ["type_voie", "nombre"]
    nb_par_type["nom"] = nb_par_type["type_voie"].map(LIBELLES_VOIES)

    fig = px.bar(
        nb_par_type,
        x="nom",
        y="nombre",
        color="nom",
        color_discrete_map=couleurs_noms,
        labels={"nom": "Type de voie", "nombre": "Nombre de tronçons"}
    )
    fig.update_layout(showlegend=False, height=400, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown("#### Les 10 lignes les plus longues")

    top_lignes = df.groupby("ligne")["longueur_km"].sum().sort_values(ascending=False).head(10).reset_index()

    fig = px.bar(
        top_lignes,
        x="longueur_km",
        y="ligne",
        orientation="h",
        labels={"longueur_km": "Longueur (km)", "ligne": "Ligne"}
    )
    fig.update_layout(height=450, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, theme=None)
