import streamlit as st
import semantic_kernel as sk

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

class TicketCreatorGuide():

    def __init__(self, groups_data: dict, deployment_name: str = "gpt-35-16k-herogra"):
        
        self.groups_data = groups_data
        self.groups = groups_data.keys()

        self.deployment_name = deployment_name

        # Define the kernel:
        self.kernel = sk.Kernel()

        deployment_name = "gpt-35-16k-herogra"
        llm = AzureChatCompletion(
            deployment_name = deployment_name, 
            endpoint = st.secrets["ENDPOINT"], 
            api_key = st.secrets["AZURE_API_KEY"]
        )

        # Add the model:
        self.kernel.add_chat_service("ticket_creator_guide", llm)

        self.TICKET_CLASSIFICATOR_GROUP_PROMPT = f"""
            Here is a ticket text: {{$input}}
            Classify the ticket in one of the following groups:
            {self.groups}
            Note1: Respond only with the group that you have classified the ticket. 
            Note2: Do not include anything else in your response.
        """

        self.classifier_group = self.kernel.create_semantic_function(
            prompt_template = self.TICKET_CLASSIFICATOR_GROUP_PROMPT,
            max_tokens = 2000
        )

    def classify_ticket(self, ticket_text: str) -> str:

        group = self.classifier_group(ticket_text)["input"]

        subgroups = self.groups_data[group]

        TICKET_CLASSIFICATOR_SUBGROUP_PROMPT = f"""
            Here is a ticket text: {{$input}}
            You know that the ticket has been classified in the group: {group}.
            Classify the ticket in one of the follwing subgroups:
            {subgroups}
            Note1: Respond only with the subgroup that you have classified the ticket. 
            Note2: Do not include anything else in your response.
        """

        classifier_subgroup = self.kernel.create_semantic_function(
            prompt_template = TICKET_CLASSIFICATOR_SUBGROUP_PROMPT,
            max_tokens = 2000
        )

        subgroup = classifier_subgroup(ticket_text)["input"]

        return (group, subgroup)