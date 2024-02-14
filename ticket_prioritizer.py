import semantic_kernel as sk
import streamlit as st
import pandas as pd
import time

from PIL import Image
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from memory_chat_utils.visualizer_utils import get_role, priority_indicator

def return_priority_score(description: str) -> int:

    kernel = sk.Kernel()
    model_name = "gpt-35-16k"
    deployment_name = f"{model_name}-herogra"
    llm = AzureChatCompletion(
        deployment_name = deployment_name, 
        endpoint = st.secrets["ENDPOINT"], 
        api_key = st.secrets["AZURE_API_KEY"]
    )

    kernel.add_chat_service("prioritizer", llm)

    prioritizer_prompt = """
        You are an assistant that helps generate scores for the priorization of the tickets
        of a deprtment. Your task is to provide a score from 1 to 3 depending on how urgent
        the ticket is. Here are the options:
        - score = 1: Tasks that are not urgent at all. Nothing critic will happen if they are not adressed for one week. Most of the tickets should be classified here.
        - score = 2: Tasks with medium urgency. These tasks should be adressed in a maximum of 3 days.
        - score = 3: Highest score, only reserved for critical tasks that if are not addressed immediately will result in critical outcomes.
        Note: Score = 3 is very exclusive for very few tickets.

        Note: Only respond with the numerical score. Do not include alologies or other explanations in your response. Do not include any words at all.
        Ticket: {{$input}}
    """

    prioritizer = kernel.create_semantic_function(prompt_template=prioritizer_prompt, max_tokens=2000)

    for attempt in range(4):
        score = prioritizer(description)["input"]

        try:
            return int(score)
        except ValueError:
            pass

        if attempt == 4:
            raise ValueError("LLm not responding. Try again in a few moments.")
        
        time.sleep(5)

def display_priority_score(score: int):
    if score <= 3:
        st.success("Low priority calculated")
    if (3 < score) & (score <= 5):
        st.warning("Medium priority calculated")
    if score == 6:
        st.error("High priority calculated")

def ticket_prioritzier(username: str) -> None:

    CT_logo = Image.open("images/CT.png")
    st.title("AI priorization assistant")
    st.write("Powered by:")
    st.image(CT_logo)

    assistant_logo = Image.open("images/robot_logo.png")

    role, _ = get_role(username)

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
            st.subheader("Hi! I'm here to help you prioritize the tickets assigned to your department")
        
        st.info("The assistant analyses the description of the ticket and creates a score weighting it with the importance of the user who has written it")

        # Give each one of the tickets a predicted priority score using the LLM:
        with st.expander(label="**Active tickets**", expanded=True):
            for _, row in tickets_data.iterrows():
                with st.spinner("Analizing the tickets..."):
                    # Calculate for each one of the rows the AI_priority_score and add it to the user score:
                    priority_score = int(return_priority_score(row["description"])) + row["user_importance_level"]

                    if row["category"] == role:
                        time.sleep(3)
                        with st.chat_message("user"):
                            st.write(row["user_importance_level"])
                            st.subheader(row["subject"])
                            st.write(row["description"])
                            st.write(f"**ID: {row['id']}**")
                            st.write(f"**Calculated priority level:**")
                            display_priority_score(priority_score)
                            st.write(row["date"])


