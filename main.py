from PIL import Image
from yaml.loader import SafeLoader
from ticket_manager import ticket_manager
from ticket_creator import ticket_creator
from plot_generator import plot_generator
from ticket_prioritizer import ticket_prioritzier

import streamlit_authenticator as stauth
import yaml
import streamlit as st

def main():

    assistant_logo = Image.open("images/robot_logo.png")
    st.set_page_config(layout="wide", page_title="Ticket manager assistant", page_icon=assistant_logo)

    with open('credentials.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:

        with st.sidebar:
            tab = st.selectbox("What funcionality are you looking for?", ["Ticket creation", "Ticket manager", "Ticket priorization", "Plot generator"])

        if tab == "Ticket manager":
            ticket_manager(name, username)

        if tab == "Ticket creation":
            ticket_creator(name)

        if tab == "Ticket priorization":
            ticket_prioritzier(username)

        if tab == "Plot generator":
            plot_generator()

    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()