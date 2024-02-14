import semantic_kernel as sk
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from memory_chat_utils.prompts import PLOT_GENERATION_TEMPLATE

class CodeGenerationAssistant:
    
    def __init__(self, data_path: str, model_name: str):
        
        # Define the kernel:
        self.kernel = sk.Kernel()

        # Define the LLM model you want to use:
        if model_name not in ["gpt-35-16k", "gpt-4-32k"]:
            raise ValueError(f"{model_name}  is an invalid model. Alowed model: ['gpt-35-16k', 'gpt-4-32k']")

        deployment_name = f"{model_name}-herogra"
        llm = AzureChatCompletion(
            deployment_name = deployment_name, 
            endpoint = st.secrets["ENDPOINT"], 
            api_key = st.secrets["AZURE_API_KEY"]
        )

        self.df_tickets = pd.read_csv(data_path)

        # Add the model, create context, initialize memory and create the semantic funcion:
        self.kernel.add_chat_service("qa", llm)

        self.qa = self.kernel.create_semantic_function(
            prompt_template = PLOT_GENERATION_TEMPLATE, 
            max_tokens = 2000
        )

    def generate_visualization_code(self, user_prompt: str) -> str:
        """
        Generates Python code for data visualization based on a user prompt.
        
        Parameters:
        - user_prompt: str - The user's request in natural language.
        
        Returns:
        - str - The generated Python code for the requested visualization.
        """
        
        # Llamar al modelo de lenguaje con el prompt
        response = self.qa(user_prompt)["input"]

        # El modelo de lenguaje debería generar un fragmento de código Python como respuesta
        python_code = response  # Asume que `response` contiene el código generado

        # Devuelve el fragmento de código Python generado
        return python_code
    
    def generate_and_execute_code(self, user_prompt):
        max_attempts = 10  # Número máximo de intentos
        attempt = 0  # Contador de intentos

        while attempt < max_attempts: #Por si el codigo que nos devuelv GPT falla, intentar corregirlo (10 intentos maximo)
            with st.spinner('Generating plot... Please wait.'):
                try:
                    # Genera código Python basado en la solicitud del usuario
                    if attempt == 0:  # Solo genera el código en el primer intento
                        python_code = self.generate_visualization_code(user_prompt)
                    python_code = python_code.replace("```python", "").replace("```", "").strip()
                    print(python_code)
                    if not self.is_code_safe(python_code):  # Verifica la seguridad del código
                        st.error("The generated code is not safe to run.")
                        break

                    # Ejecuta el código generado de forma segura
                    exec_environment = {'plt': plt, 'st': st, 'px': px, 'pd': pd, 'data': self.df_tickets}
                    
                    #print(f"\n\n\n{python_code}\n\n\n")
                    exec(python_code, exec_environment)
                    #print("The code ran successfully.")
                    break  # Sale del bucle si el código se ejecuta sin errores
                
                except Exception as e: #Si se producen errores, hay que darle feedback al gpt para que lo corriga, indicandole el error
                    error_message = str(e)
                    st.error(e)
                    #print(f"Attempt {attempt + 1}: An error occurred during execution of the generated code: {error_message}")

                    feedback_prompt = f"""
                     When trying to run the generated code to display the data, the following error occurred: {error_message}.
                     Please adjust the code to avoid this error and generate a new code snippet that works correctly.
                    """

                    # Solicita al modelo de lenguaje que genere un nuevo fragmento de código corregido utilizando el feedback_prompt
                    python_code = self.generate_visualization_code(feedback_prompt)
                    python_code = python_code.replace("```python", "").replace("```", "").strip()
                    attempt += 1  # Incrementa el contador de intentos

        if attempt == max_attempts: #Si no conseguimos generar el plot, pedirle al user un nuevo prompt.
            st.error("Error generating the plot. Try another query.")

    def is_code_safe(self, code):
        # Implementa controles de seguridad para validar el código generado
        # Esta es una parte crítica y debe hacerse con mucho cuidado
        # Por ejemplo, asegúrate de que el código no contenga llamadas a funciones peligrosas
        return True  # Esto es solo un placeholder, necesitas una implementación real aquí