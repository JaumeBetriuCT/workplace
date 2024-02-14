import streamlit as st
import pandas as pd
from PIL import Image

from memory_chat_utils.code_generation_assistant import CodeGenerationAssistant

def plot_generator():

    assistant_logo = Image.open("images/robot_logo.png")
    CT_logo = Image.open("images/CT.png")

    st.title("AI plot generator")
    st.write("Powered by:")
    st.image(CT_logo)

    # Instancia de CodeGeneratingAssistant
    code_assistant = CodeGenerationAssistant("data/tags_generation.csv", "gpt-35-16k")

    # Interfaz de usuario para la solicitud de visualización
    user_prompt = st.text_input("Describe la visualización que te gustaría ver:")

    # Botón para generar el gráfico
    generate_button = st.button("Generar Plot")

    # Variable de sesión para controlar la visualización del gráfico
    if 'show_chart' not in st.session_state:
        st.session_state.show_chart = False

    if generate_button:
        st.session_state.show_chart = True
        code_assistant.generate_and_execute_code(user_prompt)

    # Botón para generar un nuevo gráfico
    if st.session_state.show_chart:
        if st.button("Generar otro plot"):
            st.session_state.show_chart = False
            # Esto limpiará el input y permitirá al usuario ingresar una nueva solicitud
            st.experimental_rerun()