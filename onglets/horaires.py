import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def afficher(df2, fr, minutes_vers_heure, COL_DISTANCE, ACCENT, ROSE, GRENAT, icone_train_rose, icone_train_grenat):
    st.subheader("Temps de parcours : Analyse")
    st.caption("Analyse des meilleures durées de parcours entre les différentes relations ferroviaires.")

    nb_relations = df2["relations"].nunique()
    nb_annees = df2["année"].nunique()
    temps_moyen = df2["temps estimé en minutes"].mean()
    temps_min = df2["temps estimé en minutes"].min()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Relations", fr(nb_relations))
    col2.metric("Années", fr(nb_annees))
    col3.metric("Temps moyen", minutes_vers_heure(temps_moyen))
    col4.metric("Temps minimum", minutes_vers_heure(temps_min))

    st.divider()

    st.markdown("#### Rechercher une relation")

    relations = sorted(df2["relations"].dropna().unique().tolist())

    relation_selectionnee = st.selectbox("Choisir une relation", relations)

    donnees_relation = df2[df2["relations"] == relation_selectionnee].copy()

    if len(donnees_relation) > 0:
        derniere_annee = donnees_relation["année"].max()
        derniere_ligne = donnees_relation[donnees_relation["année"] == derniere_annee].iloc[0]
        temps_actuel = derniere_ligne["temps estimé en minutes"]

        a, b, c = st.columns(3)
        a.metric("Relation", relation_selectionnee)
        b.metric("Temps estimé *", minutes_vers_heure(temps_actuel))
        c.metric("Année", str(derniere_annee))
        st.caption("*Moyenne des meilleurs temps de parcours pour la relation sélectionnée.")


        st.markdown("##### Évolution du temps de parcours")

        donnees_relation = donnees_relation.sort_values("année")

        fig = px.line(
            donnees_relation,
            x="année",
            y="temps estimé en minutes",
            markers=True,
            labels={"année": "Année", "temps estimé en minutes": "Temps estimé (minutes)"}
        )
        fig.update_traces(line_color=ACCENT, marker_color=ACCENT)
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True, theme=None)

        st.markdown("##### Historique")

        historique = donnees_relation[["année", "temps estimé en minutes"]].copy()
        historique["temps"] = historique["temps estimé en minutes"].apply(minutes_vers_heure)
        historique.columns = ["Année", "Minutes", "Temps"]

        st.dataframe(historique, use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("#### Les 10 relations les plus rapides")
    st.caption("Attention : les distances de parcours ne sont pas prises en compte.")
    st.caption("La relation la plus rapide est alors PARIS-REIMS, les deux gares étant les moins éloignées du jeu de données.")

    rapides = df2.groupby("relations")["temps estimé en minutes"].min().sort_values().head(10).reset_index()

    rapides["temps"] = rapides["temps estimé en minutes"].apply(minutes_vers_heure)

    fig = px.bar(
        rapides,
        x="temps estimé en minutes",
        y="relations",
        orientation="h",
        labels={"temps estimé en minutes": "Temps minimum", "relations": "Relation"}
    )
    fig.update_layout(height=450, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, theme=None)


    st.markdown("#### Les 10 relations avec le meilleur ratio rapidité / distance (à vol d'oiseau)")
    st.caption("Mise en parallèle avec le graphe précédent : la distance est maintenant prise en compte et la réelle efficacité de parcours est évaluée." )
    st.caption("La relation PARIS - BORDEAUX est l'axe le plus performant car l'infrastructure à grande vitesse permet de relier les deux métropoles en à peine plus de deux heures. ")

    top_10 = (
        df2.assign(min_par_km=df2["temps estimé en minutes"] / df2[COL_DISTANCE])
        .groupby("relations")["min_par_km"].min()
        .reset_index().dropna().sort_values("min_par_km").head(10)
        .reset_index(drop=True)
    )
    top_10["pos"] = top_10.index          # 0..9
    x_max = top_10["min_par_km"].max() * 1.3

    # Traits
    x_lignes = [v for val in top_10["min_par_km"] for v in (0, val, None)]
    y_lignes = [p for pos in top_10["pos"] for p in (pos, pos, None)]

    fig = go.Figure([
        go.Scatter(x=x_lignes, y=y_lignes, mode="lines",
                   line=dict(color=ROSE, width=2),
                   hoverinfo="skip", showlegend=False),
        # Pts invisibles : servent au survol et aux étiquettes
        go.Scatter(x=top_10["min_par_km"], y=top_10["pos"],
                   mode="markers+text",
                   marker=dict(size=28, opacity=0),
                   text=[f"{v:.3f} min/km" for v in top_10["min_par_km"]],
                   textposition="middle right", cliponaxis=False,
                   customdata=top_10["relations"],
                   hovertemplate="%{customdata}<br>%{x:.3f} min/km<extra></extra>",
                   showlegend=False),
    ])

    # 1 icone de train au bout de chaque trait
    icone = icone_train_rose()
    for _, row in top_10.iterrows():
        fig.add_layout_image(
            source=icone,
            xref="x", yref="y",
            x=row["min_par_km"], y=row["pos"],
            sizex=x_max * 0.05, sizey=0.8,
            xanchor="center", yanchor="middle",
            sizing="contain", layer="above",
        )

    fig.update_layout(
        height=480,
        margin=dict(l=10, r=90, t=5, b=5),
        xaxis=dict(title="Temps par kilomètre (min/km)", range=[0, x_max]),
        yaxis=dict(
            tickvals=top_10["pos"], ticktext=top_10["relations"],
            range=[9.6, -0.6],  # inversé : le meilleur en haut
            title="",
        ),
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

    ############

    st.markdown("#### Les 10 relations avec le pire ratio rapidité / distance (à vol d'oiseau)")
    st.caption("Quelles performances méritent une attention concernant leur amélioration ?" )
    st.caption("La relation LYON - BORDEAUX est l'axe le moins performant ")
    st.caption("Hypothèse : le réseau français, ultra-centralisé autour de Paris, a délaissé la ligne directe historique à travers le Massif Central au profit des axes radiaux. la ligne TER reliant les deux villes est indirecte et passe par Clermont-Ferrand, ce qui rallonge considérablement le temps de parcours. ")
    top_10 = (
        df2.assign(max_par_km=df2["temps estimé en minutes"] / df2[COL_DISTANCE])
        .groupby("relations")["max_par_km"].min()
        .reset_index().dropna().sort_values("max_par_km").tail(10)
        .reset_index(drop=True)
    )
    top_10["pos"] = top_10.index          # 0..9
    x_max = top_10["max_par_km"].max() * 1.3

    # Traits
    x_lignes = [v for val in top_10["max_par_km"] for v in (0, val, None)]
    y_lignes = [p for pos in top_10["pos"] for p in (pos, pos, None)]

    fig = go.Figure([
        go.Scatter(x=x_lignes, y=y_lignes, mode="lines",
                   line=dict(color=GRENAT, width=2),
                   hoverinfo="skip", showlegend=False),
        # Pts invisibles : servent au survol et aux étiquettes
        go.Scatter(x=top_10["max_par_km"], y=top_10["pos"],
                   mode="markers+text",
                   marker=dict(size=28, opacity=0),
                   text=[f"{v:.3f} min/km" for v in top_10["max_par_km"]],
                   textposition="middle right", cliponaxis=False,
                   customdata=top_10["relations"],
                   hovertemplate="%{customdata}<br>%{x:.3f} min/km<extra></extra>",
                   showlegend=False),
    ])

    # 1 icone de train au bout de chaque trait
    icone = icone_train_grenat()
    for _, row in top_10.iterrows():
        fig.add_layout_image(
            source=icone,
            xref="x", yref="y",
            x=row["max_par_km"], y=row["pos"],
            sizex=x_max * 0.05, sizey=0.8,
            xanchor="center", yanchor="middle",
            sizing="contain", layer="above",
        )

    fig.update_layout(
        height=480,
        margin=dict(l=10, r=90, t=5, b=5),
        xaxis=dict(title="Temps par kilomètre (min/km)", range=[0, x_max]),
        yaxis=dict(
            tickvals=top_10["pos"], ticktext=top_10["relations"],
            #range=[9.6, -0.6],  # inversé : le meilleur en haut
            title="",
        ),
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

############


    st.markdown("#### Les 10 relations les plus longues")
    st.caption("PARIS - NICE est la relation la plus longue avec une distance ferroviaire de ~685 km")


    longues = df2.groupby("relations")["temps estimé en minutes"].max().sort_values(ascending=False).head(10).reset_index()

    fig = px.bar(
        longues,
        x="temps estimé en minutes",
        y="relations",
        orientation="h",
        labels={"temps estimé en minutes": "Temps maximum", "relations": "Relation"}
    )
    fig.update_traces(marker_color=ACCENT)
    fig.update_layout(height=450, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown("#### Distribution des temps de parcours")
    st.caption("De 150 à 199 minutes, la majorité des relations sont concentrées dans cette tranche de temps." )

    fig = px.histogram(
        df2,
        x="temps estimé en minutes",
        nbins=30,
        labels={"temps estimé en minutes": "Temps estimé (minutes)"}
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown("#### Temps moyen par année")
    st.caption("On constate une diminution drastique (333%) du temps de parcours moyen entre 1920 et 2020 passant de 500 à 150 minutes." )
    st.caption("Les performances des trains ont évolué grâce au passage de la vapeur à l'électricité, associé à des rames plus légères et aérodynamiques. " \
    "Ce saut technique a été maximisé par la création de lignes dédiées à grande vitesse (1981).")

    moyenne_annee = df2.groupby("année")["temps estimé en minutes"].mean().reset_index()

    fig = px.line(
        moyenne_annee,
        x="année",
        y="temps estimé en minutes",
        markers=True,
        labels={"année": "Année", "temps estimé en minutes": "Temps moyen (minutes)"}
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, theme=None)

    with st.expander("Voir toutes les données"):
        st.dataframe(df2, use_container_width=True, hide_index=True)
