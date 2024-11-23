from cProfile import label
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Broad Prosperity: Netherlands",
    layout="wide",
    initial_sidebar_state="expanded")

st.title("Brede Velvaart van het Nederland")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
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
                selected_indicator = st.selectbox("Select an indicator:", options=options)
                st.write(f"You selected: {selected_indicator}")
            else:
                st.warning("No valid indicators found in the 'label' column.")
        else:
            st.warning("The 'label' column does not exist in the DataFrame.")
    else:
        st.error("df_indicators is not a valid DataFrame.")

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

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

# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'


#######################
# Dashboard Main Panel
col = st.columns((2, 2), gap='medium')

with col[0]:
    st.markdown('''**Wat is de Brede Welvaart**''')
    st.markdown('''Brede welvaart gaat over alles wat het leven ‘de moeite waard maakt’. 
                Het gaat over inkomen en werk, maar ook over de woonkwaliteit, natuur, 
                gezondheid en het welbevinden van mensen. Dat is het uitgangspunt achter het concept 
                ‘brede welvaart’. Het is een andere manier van kijken naar de samenleving. Integraal, 
                met oog voor de samenhang tussen de factoren die er voor de inwoners toe doen.''')
                
    st.markdown('''CMO STAMM werkt aan de verbetering van de brede welvaart in het Noorden. Dit doen 
                wij door bewustwording te vergroten, het monitoren en uitvoeren van onderzoek en het 
                ontwikkelen van een visie en strategie voor beleid.''')
    
with col[1]: 
    # Define the themes and their corresponding markdown content
    themes = {
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
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Ervaren gezondheid": """
            **Welkom bij Ervaren gezondheid indicator**
            - Deze indicator is onderdeel van het Gezondheid thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Levensverwachting bevolking": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Gezondheid thema.
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Personen met één of meer langdurige ziekten of aandoeningen": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Gezondheid thema.
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Nettoarbeidsparticipatie": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Brutoarbeidsparticipatie": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Hoogopgeleide bevolking": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Werkloosheid": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Vacaturegraad": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Afstand tot ov": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Arbeid en vrije tijd thema.
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Tevredenheid met woonomgeving": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Wonen thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Tevredenheid met woning": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Wonen thema.
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Afstand tot sportterrein": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Wonen thema.
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Afstand tot basisschool": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Wonen thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Afstand tot café e.d.": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Wonen thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Contact met familie, vrienden of buren": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Samenleving thema.
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Vertrouwen in instituties": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Samenleving thema.
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Vertrouwen in anderen": """
            **Welkom bij {selected_indicator} indicator**
            -Deze indicator is onderdeel van het Samenleving thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Vrijwilligerswerk": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Samenleving thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Vaak onveilig voelen in de buurt": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Veiligheid thema.
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Aantal ondervonden delicten": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Veiligheid thema.
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Geregistreerde misdrijven": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Veiligheid thema.
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Natuurgebied per inwoner": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Milieu thema
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Emissies van fijnstof naar lucht": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Milieu thema
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Afstand tot openbaar groen": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Milieu thema
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Natuur- en bosgebieden": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Milieu thema
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Broeikasgasemissies per inwoner": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Milieu thema
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Kwaliteit van zwemwater binnenwateren": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Milieu thema
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Kwaliteit van zwemwater kustwateren": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Milieu thema
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Gemiddelde schuld per huishouden": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Economisch kapitaal
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Mediaan vermogen van huishoudens": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Economisch kapitaal
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Particuliere zonne-energie": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Natuurlijk kapitaal
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Natuur- en bosgebieden": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Natuurlijk kapitaal
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Bebouwd terrein": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Natuurlijk kapitaal
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Emissies van fijnstof naar lucht": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Natuurlijk kapitaal
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Fosfaatuitscheiding landbouw": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Natuurlijk kapitaal
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Groen-blauwe ruimte, exclusief reguliere landbouw": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Natuurlijk kapitaal
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Stikstofuitscheiding landbouw": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Natuurlijk kapitaal
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Arbeidsduur per week": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Menselijk kapitaal
            - **Feature 2:** Uses light backgrounds for better readability.
        """,
        "Hoogopgeleide bevolking": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Menselijk kapitaal
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """,
        "Ervaren gezondheid": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Menselijk kapitaal
            - **Feature 2:** A calming interface for a relaxed experience.
        """,
        "Sociale cohesie": """
            **Welkom bij {selected_indicator} indicator**
            - Deze indicator is onderdeel van het Sociaal kapitaal
            - **Feature 2:** Uses dark backgrounds to reduce eye strain.
        """
}

    # Display the markdown content based on the selected theme
    st.markdown(themes[selected_indicator], unsafe_allow_html=True)