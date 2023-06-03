import os
import csv 
import streamlit as st
from datetime import date
from datetime import datetime
import pandas as pd
import barcode
from barcode.codex import Code128
from PIL import Image
from barcode.writer import ImageWriter
import sqlite3
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from google.cloud import storage

# SETUP
st.set_page_config(page_title = 'Chargenverwaltungstool')

# Get the directory where the current script file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the current script file's directory
os.chdir(current_dir)

if st.session_state['authentication_status']:
    st.title('Chargenverwaltungstool CVTv5')
    st.header('Molekulare Diagnostik - Routine')


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

    tab1, tab2, tab3 = st.tabs(['Wareneingang', 'Produktaktivierung', 'Bestand'])

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

        def print_barcode(barcode):
            # '''print unique_id as 128 code bc'''
            # import socket

            # # Generate the ZPL code for the barcode
            # zpl_code = f'^XA^FO25,50^BY2^BCN,50,Y,N,N^FD{barcode}^FS^XZ'

            # # Print the barcode using a socket connection to the printer
            # mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # host = "172.16.16.141"
            # port = 9100

            # try:
            #     mysocket.connect((host, port))
            #     for i in range(stock_input):
            #         mysocket.send(zpl_code.encode('utf-8'))
            #     mysocket.close()
            # except:
            #     print("Error with the connection")
            return

    # Load Database
        project_id = "parabolic-env-387006"
        file_name = "db_base.db"
        bucket_name = "cvtv5"
        cur, conn = open_db(project_id)

    # Create Manufacturer list and selectbox

        cur.execute("SELECT manufacturer FROM base")
        data = cur.fetchall()
        manufacturer_list = []
        manufacturer_list = convert_single_tuple_to_list(data)  
        manufacturer_select = st.selectbox('Wählen Sie den Hersteller:', manufacturer_list)
        system_checkbox = st.checkbox('Nach Analysesystem filtern', value=False, key='system_checkbox')
        system_select = ''
        category_checkbox = st.checkbox('Nach Produkttyp filtern', value=False, key='category_checkbox')
        category_select = ''
        st.markdown('________________________________________')



        if system_checkbox:
            cur.execute("SELECT manufacturer, system FROM base")
            data = cur.fetchall()
            data_dict={}
            for x in data:
                data_dict.setdefault(x[0], set()).add(x[1])

            system_dict = data_dict
            system_list = list(system_dict[manufacturer_select])
            system_list = sorted(filter(None, system_list))
            system_select = st.selectbox('Wählen Sie das Analysesystem:', system_list)

            cur.execute("SELECT product FROM base WHERE manufacturer= ? AND system =?", (manufacturer_select, system_select,))
            data = cur.fetchall()
            product_list = convert_single_tuple_to_list(data)



        if category_checkbox:
            cur.execute("SELECT category FROM base")
            data = cur.fetchall()
            category_list = convert_single_tuple_to_list(data)
            category_select = st.selectbox('Wählen Sie den Typ:', category_list, key = 'category_select_category')
            
            cur.execute("SELECT product FROM base WHERE manufacturer= ? AND category = ?", (manufacturer_select, category_select,))
            data = cur.fetchall()
            product_list = convert_single_tuple_to_list(data)



        if system_checkbox and category_checkbox:
            cur.execute("SELECT product FROM base WHERE manufacturer= ? AND category = ? AND system = ?", (manufacturer_select, category_select, system_select))
            data = cur.fetchall()
            product_list = convert_single_tuple_to_list(data)



        if not system_checkbox and not category_checkbox:

            cur.execute("SELECT product FROM base WHERE manufacturer = ?", (manufacturer_select,))
            data = cur.fetchall() 
            product_list = convert_single_tuple_to_list(data)



        product_select = st.selectbox("Wählen Sie das Produkt", product_list, key = 'product_select_nofilter')
        st.markdown('________________________________________')
        cur.execute("SELECT category FROM base WHERE product = ?", (product_select,))
        data = cur.fetchall()
        product_category = data[0][0]
        if product_category == 'Consumable':
            lot_input = st.text_input('LOT', disabled = True, placeholder = 'Keine Eingabe notwendig')
            exp_input = st.date_input('Expiration Date', disabled = True)
        else:
            lot_input = st.text_input('LOT', placeholder='...')
            exp_input = st.date_input('Expiration Date')
        stock_input = st.number_input("Geben Sie die Anzahl Einheiten ein:", min_value=1, max_value=99, step=1)
        add_product = st.button("Produkt hinzuzufügen")
        

   
# Write inputs into DB

        if add_product:
            cur.execute("SELECT rowid, product FROM instock WHERE product = ? AND lot = ?", (product_select, lot_input,))
            conn.commit()
            upload_database_file(bucket_name, file_name, project_id)
            data = cur.fetchall()

            if not data:
                cur.execute("INSERT INTO instock (product, lot, exp_date, is_stock) VALUES (?,?,?,?)", (product_select, lot_input, exp_input, stock_input,))
                conn.commit()
                cur.execute("SELECT rowid,* FROM instock WHERE product=? AND lot=?", (product_select, lot_input,))
                data = cur.fetchall()
                rowid = data[0][0]
                cur.execute("UPDATE instock SET unique_id=?  WHERE rowid=?", (rowid+10000000, rowid))
                cur.execute("SELECT unique_id FROM instock WHERE rowid=?", (rowid,))
                data = cur.fetchone()
                barcode = str(data[0])
                conn.commit()
                upload_database_file(bucket_name, file_name, project_id)
                # print_barcode(barcode)

            else:
                cur.execute("SELECT rowid,* FROM instock WHERE product=? AND lot=?", (product_select, lot_input,))
                data = cur.fetchall()
                rowid = data[0][0]
                cur.execute("UPDATE instock SET is_stock=is_stock + ?, unique_id=?, lot=?, exp_date=?  WHERE rowid=?", (stock_input, rowid+10000000, lot_input, exp_input, rowid))
                cur.execute("SELECT unique_id FROM instock WHERE rowid=?", (rowid,))
                data = cur.fetchone()
                barcode = str(data[0])
                conn.commit()
                upload_database_file(bucket_name, file_name, project_id)
                # print_barcode(barcode)

            cur.execute("SELECT is_stock, unique_id FROM instock WHERE rowid = ?", (rowid,))
            data = cur.fetchall()
            st.success(f'Produkt erfolgreich hinzugefügt. Neuer Bestand: {data[0][0]}')
            st.info(f'Die folgende unique ID wurde vergeben: {data[0][1]}')
            printcode = Code128(barcode, writer=ImageWriter())
            png_filename = 'barcode.png'
            printcode.save(png_filename)
            png_filename += ".png"
            barcode_image = Image.open(png_filename)
            st.image(barcode_image, caption = "Generated Barcode")

    # Close Database
        conn.close()




    with tab2:
        uid_input = st.text_input('Scannen Sie den Barcode des Produkts oder geben Sie die unique ID ein:')
        uid_input_button = st.button('Produkt aktivieren')

        if uid_input_button:
            cur, conn = open_db(project_id)
            cur.execute("SELECT * FROM instock WHERE unique_id = ?", (uid_input, ))
            data = cur.fetchall()
            product_activate = convert_single_tuple_to_list(data)[0]
            cur.execute("UPDATE instock SET is_stock = is_stock - ? WHERE unique_id = ?", (1, uid_input,))
            cur.execute("SELECT * FROM instock WHERE unique_id = ?", (uid_input,) )
            data = cur.fetchall()
            in_stock_updated = list(data)
            st.write()

            st.success(f'Sie haben erfolgreich 1 Einheit {product_activate} ausgebucht. Neuer Bestand: {in_stock_updated[0][3]}')
                
            conn.commit()
            upload_database_file(bucket_name, file_name, project_id)

        conn.close()

    with tab3:   

        cur, conn = open_db(project_id)

        cur.execute("SELECT * FROM instock")
        data = cur.fetchall()
        conn.close()
        
        df = pd.DataFrame(data)
        st.dataframe(df)              

else:
    st.error('Zugriff verweigert. Bitte loggen Sie sich ein.')
