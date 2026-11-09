import streamlit as st
import pandas as pd

from data import DESCRIPTION, SOURCE, METHODOLOGIE, VARIABLES, DEF


def afficher():
    st.subheader("📚 Documentation")

    st.markdown("### Description")
    st.write(DESCRIPTION)

    st.markdown("### Sources")
    st.write(SOURCE)

    st.markdown("### Méthodologie")
    st.write(METHODOLOGIE)

    st.markdown("### Variables")

    variables = pd.DataFrame(
        list(VARIABLES.items()),
        columns=["Variable", "Description"]
    )

    st.dataframe(variables, use_container_width=True, hide_index=True)

    st.markdown("### Définitions")
    for d in DEF : st.write(d," : ", DEF[d]) 
