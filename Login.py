import os
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title = 'Chargenverwaltungstool', page_icon = './icon_med.jpeg')

# Get the directory where the current script file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the current script file's directory
os.chdir(current_dir)

st.title('Chargenverwaltungstool CVTv5')
st.header('Molekulare Diagnostik, Medics Labor AG')

# hashed_passwords = stauth.Hasher(['123', '456']).generate()
# print(hashed_passwords)

if 'authentication_status' not in st.session_state:
	st.session_state['authentication_status'] = False


# st.set_page_config(page_title = 'Chargenverwaltungstool', page_icon = './icon.jpg')
with open('./userdb.yaml') as f:
	userdb = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
	userdb['credentials'], 
	userdb['cookie']['name'], 
	userdb['cookie']['key'], 
	userdb['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
	sidebar_name = st.sidebar.text(st.session_state.name)
	authenticator.logout('Logout', 'sidebar')


	st.success(f'Welcome {name}')

elif authentication_status is False:
	st.error('Username/Passwort stimmen nicht überein')
elif authentication_status is None:
	st.warning('Bitte loggen Sie sich ein')