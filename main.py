import streamlit as st
from utils import ticket_visualizer
from utils import show_recommended_tickets
from PIL import Image

def main():
    assistant_logo = Image.open("images/robot_logo.png")

    st.set_page_config(layout="wide", page_title="Ticket manager assistant", page_icon=assistant_logo)
    st.title("Ticket manager assistant")
    user_name = "Antonio"
    role = "IT specialist (comunication aplications)"

    col1, col2 = st.columns(2)

    with col2:
        ticket_visualizer()

    with col1:
        button_pressed = st.button("Analyse tickets")
        if not button_pressed:
            with st.chat_message("user", avatar=assistant_logo):
                st.subheader(f"Hello {user_name}. \n Your role is: **{role}**")
        if button_pressed:
            with st.chat_message("user", avatar=assistant_logo):
                st.subheader(f"Hello {user_name}. \n Your role is: **{role}**")
            with st.chat_message("user", avatar=assistant_logo):
                st.subheader(f"This is the analysis of the unsolved tickets that might be of interest to you:")
            
            show_recommended_tickets(role=role)

if __name__ == "__main__":
    main()