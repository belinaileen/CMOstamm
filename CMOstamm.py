from cProfile import label
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt 

# Page configuration
st.set_page_config(
    page_title="Broad Prosperity: Netherlands",
    layout="wide",
    initial_sidebar_state="expanded")

# Create a two-line title with different styles
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

########################
#translations dictionary
translations = {
    "en": {
        "title": "Broad Prosperity Indicators",
        "welcome": "Welcome to the Prosperity Dashboard!",
        "prosperity_indicator": "Here are the prosperity indicators:",
        "language_selection": "Language Selection",
        "select_indicator": "Select an Indicator",
        "Your selection": "You selected",
    },
    "nl": {
        "title": "Indicatoren van Brede Welvaart",
        "welcome": "Welkom bij het Welvaartsdashboard!",
        "prosperity_indicator": "Hier zijn de welvaartsindicatoren:",
        "language_selection": "Taal Selectie",
        "select_indicator": "Selecteer een Indicator",
        "Your selection": "Je hebt geselecteerd.",
    },
}

translatecol0= {
    "en": {
        "What": "What is Broad Prosperity",
        #BP def stands for Broad Prosperity definition
        "BP def": '''Broad prosperity is about everything that makes life 'worthwhile'. 
             It is about income and work, but also about the quality of housing, nature, health, 
             and the well-being of people. This is the basis behind the concept of 'broad prosperity'. 
             It is a different way of looking at society. Holistically, with attention to the 
             interconnectedness of the factors that matter to the inhabitants.''',
        "cmo": '''CMO STAMM is working on improving broad prosperity in the North.
             We do this by raising awareness, monitoring and conducting research, 
             and developing a vision and strategy for policy.''',
    },
    "nl": {
        "What": "Wat is de Brede Welvaart",
        "BP def": '''Brede welvaart gaat over alles wat het leven ‘de moeite waard maakt’. 
             Het gaat over inkomen en werk, maar ook over de woonkwaliteit, natuur, 
             gezondheid en het welbevinden van mensen. Dat is het uitgangspunt achter het concept 
             ‘brede welvaart’. Het is een andere manier van kijken naar de samenleving. Integraal, 
              met oog voor de samenhang tussen de factoren die er voor de inwoners toe doen.''',
        "cmo": '''CMO STAMM werkt aan de verbetering van de brede welvaart in het Noorden. Dit doen 
             wij door bewustwording te vergroten, het monitoren en uitvoeren van onderzoek en het 
             ontwikkelen van een visie en strategie voor beleid.'''
        
                
    },
}
#######################
# Load data
#df_meta = pd.read_csv('meta.csv')
df_indicators = pd.read_csv('indicatoren.csv', delimiter=';')

#######################
# Sidebar
with st.sidebar:
    st.title('Indicatoren van brede welvaart')

    language = st.selectbox(
        "Select Language/Selecteer Taal",
        options=["en", "nl"],
        format_func=lambda x: "English" if x == "en" else "Nederlands",
    )

    lang = "en" if language == "English" else "nl"
    #using lang, the program knows which text to get from the translations dictionary

    # Check if df_indicators is a DataFrame and contains 'label'
    if isinstance(df_indicators, pd.DataFrame):
        if 'label' in df_indicators.columns:
                # Handle NaN and duplicates, then create options
            options = df_indicators['label'].dropna().unique().tolist()
            if options:  # Ensure there are valid options
                selected_indicator = st.selectbox("Select an indicator:", options=options)

                # Filter df_indicators based on the selected indicator
                filtered_df = df_indicators[(df_indicators['label'] == selected_indicator) & (df_indicators['jaar'] == 2020)]

                st.write(f"Jij hebt geselecteerd: {selected_indicator}")
            else:
                st.warning("No valid indicators found in the 'label' column.")
        else:
            st.warning("The 'label' column does not exist in the DataFrame.")
    else:
        st.error("df_indicators is not a valid DataFrame.")

    statnaam_options = filtered_df['statnaam']

    translations1 ={
        "en": {
            "Select 1st mun": "Select the first municipality:",
            "Select 2nd mun": "Select the 2nd municipality:",
        },
        "nl": {
            "Select 1st mun": "Selecteer de eerste gemeente:",
            "Select 2nd mun": "Selecteer de tweede gemeente:"
        },
    }

    selected_statnaam_1 = st.sidebar.selectbox(translations1[lang]['Select 1st mun'], statnaam_options)
    selected_statnaam_2 = st.sidebar.selectbox(translations1[lang]['Select 2nd mun'], statnaam_options)
    statnaams_filtered = filtered_df[filtered_df['statnaam'].isin([selected_statnaam_1, selected_statnaam_2])]

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
col = st.columns((2.25, 2.25, 1.5), gap='medium')

with col[0]:
    st.markdown(f"### {translatecol0[language]['What']}")
    st.markdown(translatecol0[language]['BP def'])
    st.markdown(f"**{translatecol0[language]['cmo']}**")
  
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

with col[2]:
    st.expander('About', expanded=True)

    # Filter rows based on label and year
    df_lifesatisfaction = df_indicators[
        (df_indicators['label'] == 'Tevredenheid met het leven') &  # Filter by label
        (df_indicators['jaar'] == 2020) 
    ]

    st.markdown('#### Gemeenten gerangschikt van hoog naar laag in Tevredenheid met het Leven')

    # Calculate the maximum value for 'waarde' column
    max_value = df_lifesatisfaction['waarde'].dropna().max()  # Find the max value in the 'waarde' column

    # Display the DataFrame using Streamlit
    st.dataframe(
    df_lifesatisfaction, 
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

col1 = st.columns((2.25, 2.25, 1.5), gap='medium')

with col1[0]:

    # Create the bar chart
    fig, ax = plt.subplots()
    
    for statnaam in [selected_statnaam_1, selected_statnaam_2]:
        ax.bar(selected_indicator, filtered_df['waarde'].values.flatten(), label=statnaam)

    # Customizing the plot
    ax.set_ylabel('Values')
    ax.set_title(f"Comparison between {selected_statnaam_1} and {selected_statnaam_2}")
    ax.legend()

    # Display the plot in Streamlit
    st.pyplot(fig)
