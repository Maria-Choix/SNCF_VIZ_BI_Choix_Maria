import streamlit as st
import pydeck as pdk
import plotly.express as px


def afficher(df, extraire_paths, COULEURS_HEX, couleurs_hex, LIBELLES_TYPES):
    couleurs_noms = {LIBELLES_TYPES.get(code, code): couleur for code, couleur in COULEURS_HEX.items()}

    st.subheader("Carte du réseau ferré")
    st.caption("Visualisez les différents types de voies et les lignes ferroviaires.")

    types_disponibles = sorted(df["type_voie"].dropna().unique().tolist())
    types_selectionnes = st.multiselect(
        "Types de voie",
        types_disponibles,
        default=types_disponibles,
        format_func=lambda x: LIBELLES_TYPES.get(x, x)
    )

    lignes_disponibles = ["Toutes les lignes"] + sorted(df["ligne"].dropna().unique().tolist())
    ligne_selectionnee = st.selectbox("Ligne", lignes_disponibles)

    filtre = df[df["type_voie"].isin(types_selectionnes)].copy()

    if ligne_selectionnee != "Toutes les lignes":
        filtre = filtre[filtre["ligne"] == ligne_selectionnee]

    chemins = []

    for _, row in filtre.iterrows():
        paths = extraire_paths(row["geo shape"])

        for path in paths:
            if len(path) >= 2:
                couleur = COULEURS_HEX.get(row["type_voie"], couleurs_hex["gris"]).replace("#", "")
                chemins.append({
                    "ligne": row["ligne"],
                    "type_voie": row["type_voie"],
                    "path": path,
                    "color": list(bytes.fromhex(couleur)) + [210]
                })

    if chemins:
        couche = pdk.Layer(
            "PathLayer",
            data=chemins,
            get_path="path",
            get_color="color",
            width_min_pixels=2,
            pickable=True,
            auto_highlight=True
        )

        vue = pdk.ViewState(latitude=46.6, longitude=2.4, zoom=5)

        carte = pdk.Deck(
            layers=[couche],
            initial_view_state=vue,
            map_style="dark",
            tooltip={"html": "<b>Ligne :</b> {ligne}<br><b>Type :</b> {type_voie}"}
        )

        st.pydeck_chart(carte)
    else:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")

    st.divider()

    st.markdown("#### Répartition des voies")

    col1, col2 = st.columns(2)

    with col1:
        par_type_carte = filtre["type_voie"].value_counts().reset_index()
        par_type_carte.columns = ["type_voie", "nombre"]
        par_type_carte["nom"] = par_type_carte["type_voie"].map(LIBELLES_TYPES)

        fig = px.pie(
            par_type_carte,
            values="nombre",
            names="nom",
            color="nom",
            color_discrete_map=couleurs_noms
        )
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with col2:
        longueur_carte = filtre.groupby("type_voie")["longueur_km"].sum().reset_index()
        longueur_carte["nom"] = longueur_carte["type_voie"].map(LIBELLES_TYPES)

        fig = px.bar(
            longueur_carte,
            x="longueur_km",
            y="nom",
            orientation="h",
            color="nom",
            color_discrete_map=couleurs_noms,
            labels={"longueur_km": "Longueur (km)", "nom": "Type de voie"}
        )
        fig.update_layout(showlegend=False, height=400, margin=dict(l=10, r=10, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown("#### Statistiques selon les filtres")

    statistiques = filtre.groupby("type_voie").agg(
        troncons=("type_voie", "size"),
        longueur_km=("longueur_km", "sum")
    ).reset_index()

    statistiques["type de voie"] = statistiques["type_voie"].map(LIBELLES_TYPES)
    statistiques["longueur_km"] = statistiques["longueur_km"].round(1)

    st.dataframe(
        statistiques[["type de voie", "troncons", "longueur_km"]],
        use_container_width=True,
        hide_index=True
    )
