import pandas as pd
import streamlit as st
import plotly.graph_objects as go

GRENAT = "#A8192B"
COL_T = "temps estimé en minutes"


def f1(x):
    """Nombre à 1 décimale avec virgule française."""
    return f"{x:.1f}".replace(".", ",")


def afficher(df, df2, COL_DISTANCE, nb_brut_horaires, ACCENT):
    # ---------- Calculs sur le dataset des temps de parcours ----------
    d = df2.copy()
    d["vitesse"] = d[COL_DISTANCE] / d[COL_T] * 60          # km/h à vol d'oiseau
    d = d.sort_values(["relations", "année"])
    a_min, a_max = int(d["année"].min()), int(d["année"].max())

    # Périmètre constant : les relations déjà présentes la première année
    rel_depart = d.loc[d["année"] == a_min, "relations"].unique()
    vit_panel = d[d["relations"].isin(rel_depart)].groupby("année")["vitesse"].mean()
    v0, v1 = vit_panel.iloc[0], vit_panel.iloc[-1]

    # Gain de temps par relation (première vs dernière observation)
    g = d.groupby("relations").agg(
        an0=("année", "first"), an1=("année", "last"),
        t0=(COL_T, "first"), t1=(COL_T, "last"), n=("année", "count"),
    )
    g = g[g["n"] >= 2]
    g["gain_pct"] = (1 - g["t1"] / g["t0"]) * 100

    # Dernière année : Paris vs transversales
    dl = d[d["année"] == a_max]
    est_paris = dl["relations"].str.startswith("PARIS")
    v_paris, v_transv = dl.loc[est_paris, "vitesse"].mean(), dl.loc[~est_paris, "vitesse"].mean()
    lentes = dl.nsmallest(3, "vitesse")

    # Qualité des données
    manquants = nb_brut_horaires - len(df2)
    part_manquants = manquants / nb_brut_horaires * 100

    # ---------- Calculs sur le dataset du réseau ----------
    km_tot = df["longueur_km"].sum()
    part_km_vpl = df.loc[df["type_voie"] == "VPL", "longueur_km"].sum() / km_tot * 100
    part_tr_vpl = (df["type_voie"] == "VPL").mean() * 100
    km_lignes = df.groupby("ligne")["longueur_km"].sum().sort_values(ascending=False)
    n_top = max(1, int(len(km_lignes) * 0.1))
    part_top = km_lignes.head(n_top).sum() / km_tot * 100

    # ---------- affichage ----------
    st.subheader("Insights, implications et recommandations")
    st.info(
        f"**Message clé :** la vitesse du rail français a été multipliée par {f1(v1 / v0)} "
        f"depuis {a_min}, mais par paliers, à chaque ouverture de LGV, "
        "et presque uniquement au départ de Paris."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Vitesse moyenne {a_min}", f"{v0:.0f} km/h")
    c2.metric(f"Vitesse moyenne {a_max}", f"{v1:.0f} km/h", delta=f"+{v1 - v0:.0f} km/h")
    c3.metric("Relations depuis Paris", f"{est_paris.sum()} / {len(dl)}")
    c4.metric("Écart Paris vs transversales", f"{v_paris - v_transv:.0f} km/h")

    # Insight 1
    st.markdown("#### 1. Le progrès vient par paliers")
    st.markdown(
        f"Sur les {len(rel_depart)} relations suivies depuis {a_min}, la vitesse moyenne passe de "
        f"{v0:.0f} à {v1:.0f} km/h, avec des sauts nets plutôt qu'une progression régulière."
    )
    fig = go.Figure(go.Scatter(x=vit_panel.index, y=vit_panel.values, mode="lines",
                               line=dict(color=ACCENT, width=3), name="Vitesse moyenne"))
    jalons = {1981: "LGV Sud-Est", 2001: "LGV Méditerranée", 2007: "LGV Est", 2017: "LGV Atlantique"}
    for an, nom in jalons.items():
        if a_min < an <= a_max:
            idx = vit_panel.index[abs(vit_panel.index - an).argmin()]
            fig.add_annotation(x=idx, y=vit_panel[idx], text=f"{nom} ({an})",
                               showarrow=True, ay=-45, font=dict(size=11))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10),
                      xaxis_title="Année", yaxis_title="Vitesse moyenne (km/h)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True, theme=None)
    st.caption("Périmètre constant (relations présentes dès la première année). "
               "Les années d'ouverture des LGV sont des repères externes aux données.")

    # Insight 2
    st.markdown("#### 2. Un réseau centré sur Paris")
    st.markdown(
        f"En {a_max}, **{est_paris.sum()} relations sur {len(dl)}** partent de Paris. "
        f"Elles atteignent **{v_paris:.0f} km/h** en moyenne, contre **{v_transv:.0f} km/h** "
        f"pour les {(~est_paris).sum()} liaisons transversales."
    )

    # Insight 3
    st.markdown("#### 3. Des gains très inégaux")
    st.caption(f"**{best}** a gagné {g.loc[best, 'gain_pct']:.0f} % de temps, "
                f"alors que **{worst}** n'a gagné que {g.loc[worst, 'gain_pct']:.0f} %.")

    sel = pd.concat([g.nlargest(5, "gain_pct"), g.nsmallest(5, "gain_pct")]).sort_values("gain_pct")
    fig2 = go.Figure(go.Bar(
        x=sel["gain_pct"], y=sel.index, orientation="h",
        marker_color=[GRENAT if v < 30 else ACCENT for v in sel["gain_pct"]],
        text=[f"{v:.0f} %" for v in sel["gain_pct"]], textposition="outside", cliponaxis=False,
    ))
    fig2.update_layout(height=380, margin=dict(l=10, r=40, t=20, b=10),
                       xaxis_title="Gain de temps depuis la première observation (%)", yaxis_title="")
    st.plotly_chart(fig2, use_container_width=True, theme=None)
    best, worst = g["gain_pct"].idxmax(), g["gain_pct"].idxmin()
    
    # Insigt 4
    st.markdown("#### 4. Des relations à la traîne")
    st.markdown("Les relations les plus lentes en " + str(a_max) + " : " + ", ".join(
        f"**{r['relations'].title()}** ({r['vitesse']:.0f} km/h)" for _, r in lentes.iterrows()) + ".")

    # Insight 5
    st.markdown("#### 5. Un réseau physique concentré")
    st.markdown(
        f"Le type VPL représente **{part_km_vpl:.0f} % des km** mais seulement "
        f"**{part_tr_vpl:.0f} % des tronçons**. Les {n_top} lignes les plus longues "
        f"(10 % du total) concentrent **{part_top:.0f} %** de la longueur : "
        "le nombre de tronçons est donc un mauvais indicateur d'importance."
    )

    # Implications et recommandations
    st.markdown("### Implications")
    st.markdown(
        "- Les gains de temps viennent des infrastructures nouvelles, pas d'ajustements d'horaires.\n"
        "- La performance est inégale selon les territoires : l'écart entre Paris et les liaisons "
        "transversales est net."
    )


    st.info(
        "### Recommandations (pistes d'attention)\n\n"
        "1. Cibler en priorité les liaisons transversales et les relations les plus lentes.\n"
        "2. Privilégier l'investissement en infrastructure plutôt que l'optimisation des horaires.\n"
        "3. Suivre les relations sans amélioration depuis plus de 10 ans."
    )


    # Limites
    st.markdown("### Limites")
    st.markdown(
        "- Pas de données de trafic ni de coût : impossible de hiérarchiser les investissements.\n"
        "- Distance à vol d'oiseau et meilleur temps de l'année, pas le temps moyen réel.\n"
        f"- {manquants} temps de parcours manquants sur {nb_brut_horaires} lignes "
        f"({f1(part_manquants)} %), supprimés avant analyse."
    )
