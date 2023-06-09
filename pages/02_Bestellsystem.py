import os
import csv 
import streamlit as st
from datetime import date
from datetime import datetime
import pandas as pd
from PIL import Image
import sqlite3
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from google.cloud import storage

# SETUP
st.set_page_config(page_title = 'Chargenverwaltungstool', page_icon = './icon_med.jpeg')

# Get the directory where the current script file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the current script file's directory
os.chdir(current_dir)

if st.session_state['authentication_status']:
    st.title('Chargenverwaltungstool CVTv5')
    st.header('Molekulare Diagnostik - Bestellungen')

    # Sidebar Definition
    with open('../userdb.yaml') as f:
        userdb = yaml.load(f, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
        userdb['credentials'], 
        userdb['cookie']['name'], 
        userdb['cookie']['key'], 
        userdb['cookie']['expiry_days'])

    sidebar_name = st.sidebar.text(st.session_state.name)
    authenticator.logout('Logout', 'sidebar')

    tab1, tab2, tab3 = st.tabs(['Bestellung definieren', 'Bestellung auslösen', 'Status'])

    with tab1:

        def download_database_file(bucket_name, file_name, project_id):
            storage_client = storage.Client(project=project_id)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(file_name)
            blob.download_to_filename(file_name)

        def upload_database_file(bucket_name, file_name, project_id):
            storage_client = storage.Client(project=project_id)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(file_name)
            blob.upload_from_filename(file_name)

        def open_db(project_id):
            # '''open the db and define cur and conn vars'''
            # Download the SQLite database file from Google Cloud Storage
            bucket_name = "cvtv5"
            file_name = "db_base.db"
            download_database_file(bucket_name, file_name, project_id)
            conn = sqlite3.connect("./db_base.db")
            cur = conn.cursor()
            return cur, conn

        def convert_single_tuple_to_list(data):
            '''Convert the tuple to a set and to a list and sort it alphabetically'''
            listname = [x[0] for x in data]
            listname = list(set(listname))
            listname = sorted(listname)
            return listname

        project_id = "parabolic-env-387006"
        file_name = "db_base.db"
        bucket_name = "cvtv5"
        cur, conn = open_db(project_id)
        
        cur.execute("SELECT supplier FROM base")
        data = cur.fetchall()
        supplier_list = []
        supplier_list = convert_single_tuple_to_list(data)
        supplier_list.insert(0, "Alle")

        supplier_select = st.selectbox("Wählen Sie den Lieferanten:", supplier_list)
        conn.commit()
        conn.close()

        st.markdown('________________________________________')
        
        cur, conn = open_db(project_id)
        if supplier_select == "Alle":
            cur.execute("SELECT product, target_stock FROM base")
            data_target = cur.fetchall()
            targstock_list = list(data_target)
        else:
            cur.execute("SELECT product, target_stock FROM base WHERE supplier = ?", (supplier_select, ))
            data_target = cur.fetchall()
            targstock_list = list(data_target)

        cur.execute("SELECT product, is_stock FROM instock")
        data_instock = cur.fetchall()
        instock_list = list(data_instock)

        targstock_dict = {item[0]: item[1] for item in targstock_list}

        instock_dict = {}
        for item in instock_list:
            name = item[0]
            value = item[1]

            if name in instock_dict:
                instock_dict[name] += value
            else:
                instock_dict[name] = value

        for item in targstock_dict:
            if item in instock_dict:
                st.write(item, targstock_dict[item], instock_dict[item])
            else:
                st.write(item, targstock_dict[item], "N/A")
        
        conn.commit()
        upload_database_file(bucket_name, file_name, project_id)
        conn.close()

    with tab2:
        st.text('Bestellungen auslösen')

    with tab3:
        st.text("Status")


else:
    st.error('Zugriff verweigert. Bitte loggen Sie sich ein.')
