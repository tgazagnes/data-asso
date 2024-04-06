import streamlit as st
import pandas as pd
import plotly.express as px
#from streamlit_dynamic_filters import DynamicFilters

# Page setting : wide layout
st.set_page_config(
    layout = "wide",
    page_title="Analyse subventions 2022 - Métropole de Lyon"
)

st.sidebar.caption(
    """Note méthodologique :
    Cette analyse se base uniquemement sur les données open-source publiées par l'Etat, la Métropole de Lyon, la Ville de Lyon.
    Les données présentées ici sont largement incomplètes et n'ont valeur que d'exemple.
                                      """)




st.markdown(
    """# 🔎 [Prototype] data.asso
Analyses des subventions accordées aux acteurs associatifs en 2022 (territoire : Métropole de Lyon)
"""
)
@st.cache_data
def load_data():
    df = pd.read_parquet("data/base_consolidee.parquet")
    # Copie des données pour transfo
    df_total = df.copy()
    return df_total

df_total = load_data()

# Création du filtre dynamique par niveau géographique
#niveaux_geo = ["REGION", "DEP_CODE_NOM", "LIBEPCI", "BASSIN_DE_VIE", "COMMUNE_CODE_NOM"]
#dynamic_filters = DynamicFilters(df_other, filters=niveaux_geo)
#df_other_filtre = dynamic_filters.filter_df()

tab1, tab2, tab3= st.tabs(
    [
        "Statistiques d'ensemble :trophy:",
        "Top subventions :microscope:",
        "Treemap subventions Etat :evergreen_tree:"
    ]
)


with tab1:

    # Calcul des indicateurs clés de haut de tableau avant transformation
    nb_benef = df_total["Bénéficiaire"].nunique()
    montant_total_2022 = df_total["Montant"].sum()

    #Nombre d'acteurs subventionnés & montants
    df_financeur_benef = df_total.groupby(
        ["Financeur", "Bénéficiaire"], 
        as_index = False)["Montant"].sum()


    #preparation des données
    df_financeur_global = df_financeur_benef.groupby("Financeur", as_index = False).agg({
        "Bénéficiaire" : "count",
        "Montant" : "sum"
    })
    df_financeur_global["Montant_2"] = df_financeur_global["Montant"].map('{:,.0f}'.format).str.replace(","," ") + " €"

    # Charte graphique MERTERRE :
    colors_map = {
        "Commune de Lyon": "#48BEF0",
        "Métropole de Lyon (Budget principal)": "#3DCE89",
        "Etat": "#364E74",
#        "Textile": "#C384B1",
#        "Papier": "#CAA674",
#        "Metal": "#A0A0A0",
#        "Verre": "#3DCE89",
#        "Autre": "#F3B900",
    }


#    dynamic_filters.display_filters(location="sidebar")
 
    # Ligne 1 : 2 cellules avec les indicateurs clés en haut de page
    l1_col1, l1_col2 = st.columns(2)

    # Pour avoir 3 cellules avec bordure, il faut nester un st.container dans chaque colonne (pas d'option bordure dans st.column)

    # 1ère métrique
    cell1 = l1_col1.container(border=True)
    # Trick pour séparer les milliers
    nb_benef = f"{nb_benef:,.0f}".replace(",", " ")
    cell1.metric("Nombre de structures subventionnées en 2022", f"{nb_benef}")

    # 2ème métrique 
    cell2 = l1_col2.container(border=True)
    montant_total_2022 = f"{montant_total_2022:,.0f}".replace(",", " ") + " €"
    cell2.metric("Montant total alloué en 2022 (tous financeurs)", f"{montant_total_2022}")


    # Ligne 2 : 2 graphiques en ligne : donut et bar chart matériaux
#    l2_col1, l2_col2 = st.columns(2)
#    with l2_col1:

    #Graphique à barres empliées du nombre de déchets par type


    fig = px.bar(df_financeur_global.sort_values(by = "Montant", ascending = False), x = "Montant", y="Financeur", 
                color="Financeur",
                barmode = 'stack',
                text = "Montant_2",
                title = "Montants des subventions par financeur en 2022",
                color_discrete_map=colors_map)
    fig.update_traces(textposition="inside")
    fig.update_layout(
        autosize=True,
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        showlegend=False,
        yaxis_title=None
    )
    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)

#    with l2_col2:
        #Graphique à barres empliées du nombre de déchets par type

    fig2 = px.bar(df_financeur_global.sort_values(by = "Bénéficiaire", ascending = False), x = "Bénéficiaire", y="Financeur", 
                color="Financeur",
                barmode = 'stack',
                text = "Bénéficiaire",
                title = "Nombre de structures subventionnées en 2022",
                color_discrete_map=colors_map)
    fig2.update_traces(textposition="inside")
    fig2.update_layout(
        autosize=True,
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        showlegend=False,
        xaxis_title="Nombre de structures bénéficiaires",
        yaxis_title = None
    )

    # Affichage du graphique
    st.plotly_chart(fig2, use_container_width=True)

    st.write("")
    st.caption(
        "Note : Cette analyse se base sur les structures qui ont pu être identifiées comme associatives.\
        Les jeux de données publiés par la Métropole de Lyon et la Ville de Lyon ne contiennent pas d'information sur la nature des structures,\
        les structures reconnues comme n'étant pas acteurs associatifs ont été exclues (bailleurs sociaux, ...)."
    )

    st.divider()


# Onglet 2 : 
with tab2:
    st.write("")

    df_financeur_benef = df_total.groupby(["Financeur", "Bénéficiaire"], as_index = False)["Montant"].sum().sort_values(by = "Montant", ascending=False)

    #Ajout montant total pour trier
    df_financeur_benef_total = df_financeur_benef.groupby("Bénéficiaire", as_index = False).agg({"Montant" : "sum"})

    df_financeur_benef2 = df_financeur_benef.merge(df_financeur_benef_total, on = "Bénéficiaire", how = "left")
    df_financeur_benef2 = df_financeur_benef2.sort_values(by = ["Montant_y", "Montant_x"], ascending = False)

    #Top structures subventionnées
    fig = px.bar(df_financeur_benef2.head(20), x="Montant_x", y="Bénéficiaire",
            barmode = 'stack',
            title = "Top 10 des structures subventionnées en 2022",
            color = "Financeur",
            text = "Montant_x",
            color_discrete_map=colors_map)
    

    fig.update_traces(textposition="inside")
    fig.update_layout(
        autosize=True,
        height=600,
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        showlegend=False,
        xaxis_title="Montant des subventions accordées en 2022",
        yaxis=dict(autorange="reversed"),
        yaxis_title = None
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    df_financeur_etat = df_total[df_total["Financeur"] == "Etat"].groupby(["Bénéficiaire"], as_index = False)["Montant"].sum().sort_values(by = "Montant", ascending=False)
    fig = px.treemap(df_financeur_etat, path=[px.Constant("Etat"), "Bénéficiaire"], values='Montant',
                    color='Bénéficiaire', 
#                    hover_data=['iso_alpha'],
                    color_continuous_scale='RdBu',
                    textinfo = "label+values"
#                    color_continuous_midpoint=np.average(df['lifeExp'], weights=df['pop'])
    )
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig, use_container_width=True)
