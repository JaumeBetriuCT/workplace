import pandas as pd
import streamlit as st
import datetime
import semantic_kernel as sk

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from PIL import Image
from typing import List
from prompts import TICKET_CLASSIFICATION_PROMPT, TICKET_CLASSIFICATION_PROMPT_2

def ticket_visualizer() -> None:

    assistant_logo = Image.open("images/robot_logo.png")

    initial_date, final_date = pd.to_datetime("2023-10-01"), pd.to_datetime("2023-11-30")
    dates = st.date_input(label="**Date selection**", value=(initial_date, final_date))

    # if final date is filled
    if len(dates) == 2:
        initial_date, final_date = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])

        tickets_data = pd.read_csv("data/tickets.csv")
        tickets_data = tickets_data.sort_values(by="date")
        tickets_data["date"] = pd.to_datetime(tickets_data["date"])

        tickets_data = tickets_data.loc[(initial_date <= tickets_data["date"]) & (tickets_data["date"] <= final_date)]
        
        with st.chat_message("user", avatar=assistant_logo):
            st.subheader("This are all the active tickets:")

        with st.expander(label="**Active tickets**", expanded=True):
            for _, row in tickets_data.iterrows():
                with st.chat_message("user"):
                    st.subheader(row["subject"])
                    st.write(row["description"])
                    st.write(row["date"])

def show_recommended_tickets(role: str) -> None:

    tickets_data = pd.read_csv("data/tickets.csv")
    tickets_data = tickets_data.sort_values(by="date")
    tickets_data["date"] = pd.to_datetime(tickets_data["date"])

    kernel_classifier = sk.Kernel()
    kernel_classifier.add_chat_service(
        "ticket classifier",
        OpenAIChatCompletion("gpt-3.5-turbo", st.secrets["OPENAI_API_KEY"])
    )

    ticket_classifier = kernel_classifier.create_semantic_function(TICKET_CLASSIFICATION_PROMPT_2)

    with st.expander(label="**Tickets of interest**", expanded=True):
        for _, row in tickets_data.iterrows():
            with st.spinner("Analizing the tickets..."):
                subject_and_description = row["subject"] + row["description"]
                print("Trying to classify the ticket")
                classification_ticket = ticket_classifier(subject_and_description)["input"]
                print("Ticket classified")
                print(classification_ticket)
                if classification_ticket == role:
                    with st.chat_message("user"):
                        st.subheader(row["subject"])
                        st.write(row["description"])
                        st.write(row["date"])


