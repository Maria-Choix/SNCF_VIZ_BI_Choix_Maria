import streamlit as st

def afficher():
    st.subheader("Problématique : comment la performance du rail français a-t-elle évolué, "
        "et quelles relations ou lignes méritent l'attention des décideurs visant l'amélioration des performances de vitesse de parcours des trains?")

    st.markdown("Public : décideurs de l’aménagement ferroviaire (voyageurs) et des transports (État, régions, SNCF **Réseau**)")

    st.markdown("**Questions d'analyse :**")
    st.markdown("- Quelle est la structure du réseau ?\n"
                "- Comment les temps de parcours ont-ils évolué ?\n"
                "- Quelles relations sont les plus efficaces, lesquelles sont à la traîne ?")
    st.markdown("**Données :** voies du Réseau Ferré National (SNCF Réseau) et meilleurs temps de parcours (1920‑2019).")