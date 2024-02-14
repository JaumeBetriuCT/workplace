from typing import Tuple
import streamlit as st
# from openai import AzureOpenAI
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import semantic_kernel as sk

class TicketTagsExtractor:
    
    def __init__(self, deployment_name: str = "gpt-35-16k-herogra"):
        self.deployment_name = deployment_name

        # Define the kernel:
        self.kernel = sk.Kernel()

        deployment_name = "gpt-35-16k-herogra"
        llm = AzureChatCompletion(
            deployment_name = deployment_name, 
            endpoint = st.secrets["ENDPOINT"], 
            api_key = st.secrets["AZURE_API_KEY"]
        )

        # Add the model, create context, initialize memory and create the semantic funcion:
        self.kernel.add_chat_service("extractor", llm)

        self.TAG_EXTRACTOR_PROMPT = """
            Here is a ticket text: {{$input}}. What are the relevant tags or key topics in this ticket that relate directly to the type of issue, classification of the problem, or category of the ticket?
            NOTES:
            1.The response must be only a list (["tag1", "tag2", "tag3", ... ] with the tags inside.
            2.If the information provided is empty, return a empty list "[]". 
            3.Don't use your inside knowledge to answer the question if the information is empty.  
        """

        self.extractor = self.kernel.create_semantic_function(
            prompt_template = self.TAG_EXTRACTOR_PROMPT,
            max_tokens = 2000
        )
    
    def extract_tags(self, ticket_text: str) -> str:

        response = self.extractor(ticket_text)["input"]

        return response

if __name__ == "__main__":
    deployment_name = "gpt-35-16k-herogra"  # Nombre de tu despliegue en Azure
    extractor = TicketTagsExtractor(deployment_name)
    
    ticket_text = """
    My computer has been running slowly, and software applications take a long time to open and respond. Can you please help improve the overall performance of my system?    
    """
    tags = extractor.extract_tags(ticket_text)
    print(tags)