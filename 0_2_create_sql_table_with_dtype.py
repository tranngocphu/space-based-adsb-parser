"""
PCAP ADSB DATA PARSER FOR SQL SERVER - SCRIPT 01

Date: 13 March 2020
Author: Phu Tran
Affiliation: 
    Air Traffic Management Research Institute
    Nanyang Technological Univerity
    Singapore
Email: phutran@ntu.edu.sg

THIS SCRIPT PERFORMS:
    1. Create a ORIGINAL_DATA table that contains all fields from the pcap files.

    2. DATETIME column is newly contructed by combining the date of the traffic
        (from pcap file name) and the seconds from midnight in the data.
    3. Data fields under IRE (Reserved Expansion) from pcap are ignored for now
"""

import pymysql
import pandas as pd
import os
import re

from constants import FIELD_PATH
from config import SQL_CON


con = pymysql.connect(
    host=SQL_CON['HOST'], 
    port=SQL_CON['PORT'], 
    user=SQL_CON['USER'], 
    password=SQL_CON['PWD'], 
    db=SQL_CON['DATABASE'], 
    autocommit=True, local_infile=True)

print('Connected to {} in {}'.format(SQL_CON['DATABASE'], SQL_CON['HOST']))

cursor = con.cursor()

table_name = 'TRACKS_2020_03'

field_data_file = os.path.join(FIELD_PATH, 'asterix_cat021_2_4_dtype.csv')
field_df = pd.read_csv(field_data_file)

for idx, field in field_df.iterrows():
    if any(substring in field.field_name for substring in ['IRE', 'ISP', '__FX__val']):
        continue
    sql = 'ALTER TABLE {} ADD COLUMN {} {};'.format(table_name, field.field_name, field.data_type)    
    cursor.execute(sql)    
    sql = 'ALTER TABLE {} MODIFY COLUMN {} {} COMMENT \'{}\';'.format(table_name, field.field_name, field.data_type, field.description)
    cursor.execute(sql)

sql = 'CREATE INDEX Callsign ON {} (I170__TId__val);'.format(table_name)
cursor.execute(sql)
sql = 'CREATE INDEX Date ON {} (Date);'.format(table_name)
cursor.execute(sql)
sql = 'ALTER TABLE {} ADD CONSTRAINT Date_Time_Callsign UNIQUE (Date,I073__time_reception_position__val,I170__TId__val);'.format(table_name)
cursor.execute(sql)