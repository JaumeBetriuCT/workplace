import pandas as pd
import streamlit as st
import ast
import semantic_kernel as sk
import json

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from PIL import Image
from memory_chat_utils.classification_prompts import TICKET_CLASSIFICATION_PROMPT, TICKET_CLASSIFICATION_PROMPT_2
from memory_chat_utils.semantic_query_engine import SemanticQueryEngine
from memory_chat_utils.ticketstagsextractor import TicketTagsExtractor

def ticket_visualizer(role: str) -> None:

    assistant_logo = Image.open("images/robot_logo.png")

    initial_date, final_date = pd.to_datetime("2024-01-01"), pd.to_datetime("2024-12-30")
    dates = st.date_input(label="**Date selection**", value=(initial_date, final_date))

    # if final date is filled
    if len(dates) == 2:
        initial_date, final_date = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])

        tickets_data = pd.read_csv("data/definitive_tickets.csv")
        tickets_data = tickets_data.sort_values(by="date")
        tickets_data["date"] = pd.to_datetime(tickets_data["date"])

        tickets_data = tickets_data.loc[(initial_date <= tickets_data["date"]) & (tickets_data["date"] <= final_date)]
        
        with st.chat_message("user", avatar=assistant_logo):
            st.subheader("This are all the active tickets:")

        with st.expander(label="**Active tickets**", expanded=True):
            st.write(role)
            for _, row in tickets_data.iterrows():
                if row["category"] == role:
                    with st.chat_message("user"):
                        st.subheader(row["subject"])
                        st.write(row["description"])
                        st.write(f"**ID: {row['id']}**")
                        priority_indicator(row["priority"])
                        st.write(row["date"])

def show_recommended_tickets(role: str, subrole: str, suggest: bool) -> None:

    tickets_data = pd.read_csv("data/definitive_tickets.csv")
    tickets_data = tickets_data.loc[tickets_data["category"] == role]
    tickets_data = tickets_data.sort_values(by="date")
    tickets_data["date"] = pd.to_datetime(tickets_data["date"])

    llm = AzureChatCompletion(
        deployment_name = "gpt-35-16k-herogra", 
        endpoint = st.secrets["ENDPOINT"], 
        api_key = st.secrets["AZURE_API_KEY"]
    )

    kernel_classifier = sk.Kernel()
    kernel_classifier.add_chat_service(
        "ticket classifier",
        llm
    )

    ticket_classifier = kernel_classifier.create_semantic_function(TICKET_CLASSIFICATION_PROMPT_2)

    semantic_query_engine = SemanticQueryEngine(data_path = "", model_name = "gpt-35-16k")
    extractor = TicketTagsExtractor()

    with st.expander(label="**Tickets of interest**", expanded=True):
        for _, row in tickets_data.iterrows():
            with st.spinner("Analizing the tickets..."):
                subject_and_description = row["subject"] + row["description"]
                print("Trying to classify the ticket")
                classification_ticket = ticket_classifier(subject_and_description)["input"]
                print("Ticket classified")
                print(classification_ticket)
                if classification_ticket == subrole:
                    with st.chat_message("user"):
                        st.subheader(row["subject"])
                        st.write(row["description"])
                        st.write(f"**ID: {row['id']}**")
                        priority_indicator(row["priority"])
                        st.write(row["date"])

                        if suggest:
                            st.write("**Suggestion AI:**")
                            st.write(
                                semantic_query_engine.execute_query(subject_and_description)
                            )
                            st.write("**Extracted tags:**")
                            tags_list = ast.literal_eval(extractor.extract_tags(subject_and_description))
                            st.write(", ".join(tags_list))

def get_role(user: str) -> str:

    with open("data/roles.json", "r") as file:
        roles = json.load(file)

    user_roles = roles[user]
    role = user_roles[0]
    subrole = user_roles[1]
        
    return (role, subrole)

def priority_indicator(priority):
    if priority == "Low priority":
        st.success("Low priority")
    if priority == "Medium priority":
        st.warning("Medium priority")
    if priority == "High priority":
        st.error("High priority")

