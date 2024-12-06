from cProfile import label
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import pydeck as pdk  # For map visualization
import geopandas as gpd
import geojson 
import folium
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="Broad Prosperity: Netherlands",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown("""
<div style='text-align: left; padding: 10px;'>
    <h1 style='color: #eb1d9c; font-size: 48px; font-weight: bold; margin-bottom: 0;'> cmo stamm.</h1>
    <h2 style='color: black; font-size: 32px; font-weight: bold; margin-top: 0;'>Brede welvaart van het Nederland</h2>
</div>
""", unsafe_allow_html=True)

#######################
# CSS styling
st.markdown("""
<style>
/* Customize sidebar */
[data-testid="stSidebar"] {
    background-color: #149bed; /* blue background */
    padding: 10px; /* Add some padding for neatness */
}
            
[data-testid="stSidebar"] h1 {
    color: #ffffff; /* Customize white sidebar title color */
    font-weight: bold;
}

.stApp [data-testid="block-container"] {
    padding-left: 0rem;
    padding-right: 0rem;
    padding-top: 0rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
    background-color: #cce1ee !important; /* Light blue background */
}
</style>
""", unsafe_allow_html=True)

#######################
# Load data
#df_meta = pd.read_csv('meta.csv')
df_indicators = pd.read_csv('indicatoren.csv', delimiter=';')

#######################
# Sidebar
with st.sidebar:
    st.title('Indicatoren van brede welvaart')
    # Check if df_indicators is a DataFrame and contains 'label'
    if isinstance(df_indicators, pd.DataFrame):
        if 'label' in df_indicators.columns:
                # Handle NaN and duplicates, then create options
            options = df_indicators['label'].dropna().unique().tolist()
            if options:  # Ensure there are valid options
                selected_indicator = st.selectbox("Selecteer een indicator:", options=options)
                st.write(f"Jij geselecteerd: {selected_indicator}")
            else:
                st.warning("No valid indicators found in the 'label' column.")
        else:
            st.warning("The 'label' column does not exist in the DataFrame.")
    else:
        st.error("df_indicators is not a valid DataFrame.")

#######################
# Plots

# Heatmap
def make_heatmap(df_reshaped, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_y).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Choropleth map
import plotly.express as px

def make_choropleth(df_reshaped, geojson, input_column, selected_color_theme):
    """
    Create a choropleth for regions in the Netherlands.
    
    Parameters:
        df_reshaped (DataFrame): The dataframe containing data.
        geojson (dict): GeoJSON data for Netherlands regions.
        region_column (str): The column in `df_reshaped` that matches the GeoJSON region IDs.
        input_column (str): The column to visualize.
        input_color_theme (str): Color scale for visualization.
    
    Returns:
        plotly.graph_objs._figure.Figure: The choropleth map.
    """
    choropleth = px.choropleth(
        df_reshaped,
        geojson=geojson,
        locations='Region',
        color='Property type: multi-family homes_2',
        color_continuous_scale=selected_color_theme,
        range_color=(0, df_reshaped['Property type: multi-family homes_2'].max()),
        featureidkey="properties.<geojson-region-key>"  # Replace <geojson-region-key> with the GeoJSON region identifier key
    )
    
    choropleth.update_geos(
        fitbounds="locations",
        visible=False
    )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


# Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

#######################
# Dashboard Main Panel
col = st.columns((2.25, 2.25, 1.5), gap='medium')

with col[0]:
    st.markdown("### Wat is de Brede Welvaart")
    st.markdown('''
    Brede welvaart gaat over alles wat het leven ‘de moeite waard maakt’. 
    Het gaat over inkomen en werk, maar ook over de woonkwaliteit, natuur, 
    gezondheid en het welbevinden van mensen. Dat is het uitgangspunt achter het concept 
    ‘brede welvaart’. Het is een andere manier van kijken naar de samenleving. Integraal, 
    met oog voor de samenhang tussen de factoren die er voor de inwoners toe doen.
    ''')
    st.markdown('''
    CMO STAMM werkt aan de verbetering van de brede welvaart in het Noorden. Dit doen 
    wij door bewustwording te vergroten, het monitoren en uitvoeren van onderzoek en het 
    ontwikkelen van een visie en strategie voor beleid.
    ''')
  
with col[1]: 
    # Define the themes and their corresponding markdown content
    Themes = {
        "Tevredenheid met het leven": """
        **Welkom bij Tevredenheid met het leven indicator**
        - Deze indicator is onderdeel van het Subjectief welzijn thema.
        - Voorlopige cijfers. Bij het toevoegen van een nieuw jaar schat 
        het model alle jaren uit de reeks opnieuw. Raadpleeg de Technische 
        Toelichting voor meer uitleg over de interpretatie van de modelschattingen 
        en de marges.
    """,
    "Tevredenheid met vrije tijd": """
        **Welkom bij Tevredenheid met vrije tijd indicator**
        - Deze indicator is onderdeel van het Subjectief welzijn thema.
        - Voorlopige cijfers. Bij het toevoegen van een nieuw jaar schat het 
        model alle jaren uit de reeks opnieuw. Raadpleeg de Technische Toelichting 
        voor meer uitleg over de interpretatie van de modelschattingen en de marges.
    """,
    "Mediaan besteedbaar inkomen": """
        **Welkom bij Mediaan besteedbaar inkomen indicator**
        - Deze indicator is onderdeel van het Materiële welvaart
        - 2021 zijn voorlopige cijfers en de correctie voor de prijsverandering 
        in 2021 is gebaseerd op de onderzoeksreeks consumentenprijzen, die de daadwerkelijk 
        betaalde energieprijzen gebruikt. Deze sluit gemiddeld genomen meer aan bij de 
        prijsontwikkeling die de bevolking heeft ervaren dan de consumentenprijsindex.
    """,
    "Bruto binnenlands product": """
        **Welkom bij Bruto binnenlands product indicator**
        - Deze indicator is onderdeel van het Materiële welvaart thema.
        - 2022 cijfers zijn voorlopig
    """,
    "Overgewicht": """
        **Welkom bij Overgewicht indicator**
        - Deze indicator is onderdeel van het Gezondheid thema.
        - Voor de jaren 2012 en 2016 is de gemeten populatie 19+
    """,
    "Ervaren gezondheid": """
        **Welkom bij Ervaren gezondheid indicator**
        - Deze indicator is onderdeel van het Gezondheid thema.
        - Voor de jaren 2012 en 2016 is de gemeten populatie 19+
    """,
    "Levensverwachting bevolking": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Gezondheid thema.
        - Gemiddelde levensverwachting over periode 2018-2021, niet apart per jaar bepaald
    """,
    "Personen met één of meer langdurige ziekten of aandoeningen": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Gezondheid thema.
        - Voor de jaren 2012 en 2016 is de gemeten populaite 19+
    """,
    "Nettoarbeidsparticipatie": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
    """,
    "Brutoarbeidsparticipatie": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
    """,
    "Hoogopgeleide bevolking": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
    """,
    "Werkloosheid": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
    """,
    "Vacaturegraad": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
        - 2021 en 2022 zijn voorlopige cijfers
    """,
    "Afstand tot ov": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
    """,
    "Tevredenheid met woonomgeving": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Wonen thema.
    """,
    "Tevredenheid met woning": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Wonen thema.
    """,
    "Afstand tot sportterrein": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Wonen thema.
    """,
    "Afstand tot basisschool": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Wonen thema.
    """,
    "Afstand tot café e.d.": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Wonen thema.
    """,
    "Contact met familie, vrienden of buren": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Samenleving thema.
        - Voorlopige cijfers. Bij het toevoegen van een nieuw jaar schat het model alle jaren uit de reeks opnieuw. Raadpleeg de Technische Toelichting voor meer uitleg over de interpretatie van de modelschattingen en de marges.
    """,
    "Vertrouwen in instituties": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Samenleving thema.
        - Voorlopige cijfers. Bij het toevoegen van een nieuw jaar schat het model alle jaren uit de reeks opnieuw. Raadpleeg de Technische Toelichting voor meer uitleg over de interpretatie van de modelschattingen en de marges.
    """,
    "Vertrouwen in anderen": """
        **Welkom bij {selected_indicator} indicator**
        -Deze indicator is onderdeel van het Samenleving thema.
        -Voorlopige cijfers. Bij het toevoegen van een nieuw jaar schat het model alle jaren uit de reeks opnieuw. Raadpleeg de Technische Toelichging voor meer uitleg over de interpretatie van de modelschattingen en de marges.
    """,
    "Vrijwilligerswerk": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Samenleving thema.
        - Voorlopige cijfers. Bij het toevoegen van een nieuw jaar schat het model alle jaren uit de reeks opnieuw. Raadpleeg de Technische Toelichging voor meer uitleg over de interpretatie van de modelschattingen en de marges.
    """,
    "Vaak onveilig voelen in de buurt": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Veiligheid thema.
    """,
    "Aantal ondervonden delicten": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Veiligheid thema.
    """,
    "Geregistreerde misdrijven": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Veiligheid thema.
        - 2021 en 2022 zijn voorlopige cijfers
    """,
    "Natuurgebied per inwoner": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Milieu thema
    """,
    "Emissies van fijnstof naar lucht": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Milieu thema
    """,
    "Afstand tot openbaar groen": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Milieu thema
    """,
    "Natuur- en bosgebieden": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Milieu thema
    """,
    "Broeikasgasemissies per inwoner": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Milieu thema
        - De gehele reeks is aangepast vanwege de nieuwe IPCC voorschriften.
    """,
    "Kwaliteit van zwemwater binnenwateren": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Milieu thema
    """,
    "Kwaliteit van zwemwater kustwateren": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Milieu thema
    """,
    "Gemiddelde schuld per huishouden": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Economisch kapitaal
        - 2022 zijn voorlopige cijfers en de correctie voor de prijsverandering in 2021 en 2022 is gebaseerd op de onderzoeksreeks consumentenprijzen, die de daadwerkelijk betaalde energieprijzen gebruikt. Deze sluit gemiddeld genomen meer aan bij de prijsontwikkeling die de bevolking heeft ervaren dan de consumentenprijsindex.
    """,
    "Mediaan vermogen van huishoudens": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Economisch kapitaal
        - 2021 zijn voorlopige cijfers en de correctie voor de prijsverandering in 2021 is gebaseerd op de onderzoeksreeks consumentenprijzen, die de daadwerkelijk betaalde energieprijzen gebruikt. Deze sluit gemiddeld genomen meer aan bij de prijsontwikkeling die de bevolking heeft ervaren dan de consumentenprijsindex.
    """,
    "Particuliere zonne-energie": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Natuurlijk kapitaal
        - cijfers 2021 en 2022 zijn voorlopig
    """,
    "Natuur- en bosgebieden": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Natuurlijk kapitaal
    """,
    "Bebouwd terrein": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Natuurlijk kapitaal
    """,
    "Emissies van fijnstof naar lucht": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Natuurlijk kapitaal
    """,
    "Fosfaatuitscheiding landbouw": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Natuurlijk kapitaal
    """,
    "Groen-blauwe ruimte, exclusief reguliere landbouw": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Natuurlijk kapitaal
    """,
    "Stikstofuitscheiding landbouw": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Natuurlijk kapitaal
    """,
    "Arbeidsduur per week": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Menselijk kapitaal
        - 2021 en 2022 zijn voorlopige cijfers
    """,
    "Hoogopgeleide bevolking": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Menselijk kapitaal
    """,
    "Ervaren gezondheid": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Menselijk kapitaal
        - Voor de jaren 2012 en 2016 is de gemeten populatie 19+
    """,
    "Sociale cohesie": """
        **Welkom bij {selected_indicator} indicator**
        - Deze indicator is onderdeel van het Sociaal kapitaal
    """
}
    if selected_indicator:
        st.markdown(Themes[selected_indicator])
    
with col[2]:
    st.expander('About', expanded=True)

    # Filter rows based on label and year
    df_selectedindicator = df_indicators[
        (df_indicators['label'] == selected_indicator) &  # Filter by label
        (df_indicators['jaar'] == df_indicators['jaar'].max())
    ]
    # Ensure the resulting dataset includes the 'label', 'jaar', and 'waarde' columns
    columns_to_include = ['label', 'jaar', 'waarde','statnaam']
    df_selectedindicator = df_selectedindicator[columns_to_include]

    df_selectedindicator_sorted = df_selectedindicator.sort_values(by='waarde', ascending=True)

    df_selectedindicator_sorted = df_selectedindicator_sorted[columns_to_include]

    st.markdown('#### Gemeenten gerangschikt van hoog naar laag in Tevredenheid met het Leven')

    if df_selectedindicator_sorted.empty:
        st.warning("Geen gegevens beschikbaar voor de geselecteerde indicator.")
    else:
        # Display the DataFrame using Streamlit
        st.dataframe(
        df_selectedindicator_sorted, 
        column_order=("statnaam", "waarde"), 
        hide_index=True, 
        width=None, 
        column_config={
            "statnaam": st.column_config.TextColumn(
                "Statnaam",
            ),
            "waarde": st.column_config.TextColumn(
                "Waarde",  # This will now display as plain numbers
            ),
        }
    )


    with st.expander('About', expanded=True):
        st.write('''
            - Data: [CBS data: Nederland (https://www.cbs.nl/nl-nl/visualisaties/regionale-monitor-brede-welvaart/indicator)]''')

col1 = st.columns((3, 3), gap='medium')

df_gd = df_selectedindicator[
        (df_selectedindicator['statnaam'].isin(['Groningen', 'Drenthe']))  # Filter by statnaam
    ]

#Groningen map
with col1[0]:
    st.markdown('**Groningen**')
   # Load GeoJSON
    geojson_file = "Indicator_01_KL_OK_11.geojson"
    with open(geojson_file) as f:
        geojson_data = geojson.load(f)

    # Center map on an initial location (change coordinates as needed)
    m = folium.Map(location=[53.2194, 6.5665], zoom_start=10)  # Example: Amsterdam

    # Add GeoJSON to the map
    folium.GeoJson(geojson_data, name="geojson").add_to(m)

    # Display the map in Streamlit
    st_folium(m, width=700, height=500)

# Drenthe map
with col1[1]:
    st.markdown('**Drenthe**')
   # Load GeoJSON
    geojson_file = "Indicator_01_KL_OK_11.geojson"
    with open(geojson_file) as f:
        geojson_data = geojson.load(f)

    # Center map on an initial location (change coordinates as needed)
    m = folium.Map(location=[52.9476, 6.6231], zoom_start=10)  

    # Add GeoJSON to the map
    folium.GeoJson(geojson_data, name="geojson").add_to(m)

    # Display the map in Streamlit
    st_folium(m, width=700, height=500)
