from PIL import Image
from memory_chat_utils.ticket_creator_guide import TicketCreatorGuide
from memory_chat_utils.semantic_query_engine import SemanticQueryEngine

import streamlit as st
import json
import time
import uuid
import csv

def ticket_creator(name):

    assistant_logo = Image.open("images/robot_logo.png")
    CT_logo = Image.open("images/CT.png")

    st.title("AI ticket creator")
    st.write("Powered by:")
    st.image(CT_logo)

    with open("data/groups_data.json", 'r') as file:
        groups_data = json.load(file)
    groups = groups_data.keys()

    with st.chat_message("user", avatar=assistant_logo):
        st.subheader(f"Welcome, {name}! I'm here to guide you through creating your ticket")

    restart = st.button("New ticket")
    if restart:
        st.rerun()

    with st.form("ticket_creation_form"):
        with st.spinner(2):
            st.info("For a smooth resolution, kindly detail your issue clearly and concisely and select the appropriate group and subgroup categories for your ticket")
        
        ticket = st.text_area("Ticket description")

        col3, col4 = st.columns(2)
        with col3:
            group = st.selectbox("Select the group", options=groups, index=None)
            subgroup = None
            if group:
                with col4:
                    subgroups = groups_data[group]
                    subgroup = st.selectbox("Select the subgroup", options=subgroups, index=None)

        send_ticket = st.toggle('Submit ticket')
        submitted = st.form_submit_button("Review/Send")

    if (submitted) & (group is not None) & (subgroup is not None) & (not send_ticket):
        ticket_creator_guide = TicketCreatorGuide(groups_data)
        semantic_query_engine = SemanticQueryEngine(data_path="", model_name="gpt-35-16k", mode="suggest")

        with st.chat_message("user", avatar=assistant_logo):

            with st.spinner("AI checking"):
                time.sleep(2)

                st.write("Try this suggestion before sending the ticket:")
                st.write(semantic_query_engine.execute_query(ticket))

                predicted_group, predicted_subgroup = ticket_creator_guide.classify_ticket(ticket)

        if (group == predicted_group) & (subgroup == predicted_subgroup):
            with st.chat_message("user", avatar=assistant_logo):
                st.success("The ticket appears to have a correct group and subgroup! If the suggestion has not resolved your issue review the ticket and select the option 'Submit ticket'.")

        if (group != predicted_group) & (subgroup != predicted_subgroup):
            with st.chat_message("user", avatar=assistant_logo):
                st.warning(f"Your chosen group is **{group}**, but our system suggests that the ticket may be better suited for the subgroup **{predicted_group}**. We recommend reviewing it before finalizing the submission.")

        if (group == predicted_group) & (subgroup != predicted_subgroup):
            with st.chat_message("user", avatar=assistant_logo):
                st.warning(f"Your chosen subgroup is **{subgroup}**, but our system suggests that the ticket may be better suited for the subgroup **{predicted_subgroup}**. We recommend reviewing it before finalizing the submission.")

    if send_ticket:
        ticket_id = uuid.uuid4()

        with st.spinner("Saving ticket..."):
            time.sleep(1)

            with open('data/saved_tickets.csv', mode='a', newline='') as csv_file:
                fieldnames = ['id', 'user', 'ticket', 'group', 'subgroup']  # Replace with your column names
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                # Replace 'your_dict' with the dictionary you want to add
                your_dict = {'id': ticket_id, 'user': name, 'ticket': ticket, 'group': group, 'subgroup': subgroup}

                # Write the dictionary as a new row in the CSV file
                writer.writerow(your_dict)

        with st.chat_message("user", avatar=assistant_logo):
            st.success(f"Congratulations! Your ticket has been successfully submitted with the id **{ticket_id}**. Expect to hear from us very shortly.")