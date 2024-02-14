import pandas as pd
import plotly.express as px
import ast
import streamlit as st

# st.set_page_config(layout="wide", page_title="Ticket manager assistant")


def create_plots():

    col1, col2 = st.columns(2)

    # Cargar los datos desde el archivo CSV
    df_tickets = pd.read_csv("/home/leibniz/Desktop/worplace/data/tags.csv")

    # Convertir la columna 'tags' de tipo string a listas reales
    df_tickets['tags'] = df_tickets['tags'].apply(ast.literal_eval)

    # Crear un DataFrame para contar la frecuencia de cada tag (excluyendo "urgent")
    tag_counts = pd.Series([tag for sublist in df_tickets['tags'] for tag in sublist if tag.lower() != 'urgent']).value_counts().reset_index()
    tag_counts.columns = ['Tag', 'Number of incidents']

    # Especifica cuántos tags quieres mostrar inicialmente
    tags_iniciales = 10

    # Crear un gráfico de barras con Plotly (excluyendo "urgent")
    fig = px.bar(tag_counts, x='Tag', y='Number of incidents', title='Distribution of Tags in Tickets',
                template='plotly_dark', width=800, height=600)

    # Configura el rango inicial del eje X para mostrar solo los primeros 10 valores
    fig.update_xaxes(range=[0, tags_iniciales])

    with col1:
        # Mostrar el primer gráfico utilizando st.plotly_chart
        st.plotly_chart(fig)

    # Crear otro tipo de gráfico (por ejemplo, un gráfico de pastel) con Plotly para los 5 tags principales (excluyendo "urgent")
    # Aquí puedes personalizar el nuevo gráfico según tus necesidades
    fig2 = px.pie(tag_counts[:5], names='Tag', values='Number of incidents', title='Top 5 Tags Distribution', width=800, height=600)

    with col2:
        # Mostrar el segundo gráfico utilizando st.plotly_chart
        st.plotly_chart(fig2)

    # Crear un tercer gráfico de barras que muestra el recuento de tickets "Urgent" vs. "No Urgent"
    urgent_counts = df_tickets['tags'].apply(lambda tags: 'urgent' in [tag.lower() for tag in tags]).value_counts().reset_index()
    urgent_counts.columns = ['Urgency', 'Number of Tickets']

    # Personaliza los nombres de las categorías
    urgent_counts['Urgency'] = urgent_counts['Urgency'].map({True: 'Urgent', False: 'No Urgent'})

    # Define los colores para "Urgent" y "No Urgent"
    colors = {'Urgent': 'red', 'No Urgent': 'blue'}

    # Crea el gráfico de barras horizontal más pequeño con colores personalizados
    fig3 = px.bar(urgent_counts, x='Number of Tickets', y='Urgency', title='Urgent vs. No Urgent Tickets',
                orientation='h', template='plotly_dark', width=600, height=275, color='Urgency', color_discrete_map=colors)

    # Oculta la leyenda
    fig3.update_layout(showlegend=False)

    with col1:
        # Mostrar el tercer gráfico utilizando st.plotly_chart
        st.plotly_chart(fig3)
