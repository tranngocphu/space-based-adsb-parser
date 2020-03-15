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

table_name = 'ORIGINAL_DATA'

field_data_file = os.path.join(FIELD_PATH, 'asterix_cat021_2_4_dtype.csv')
field_df = pd.read_csv(field_data_file)

with open(os.path.join(FIELD_PATH, 'field_list_sql.txt'), 'w') as f1, open(os.path.join(FIELD_PATH, 'field_list_sql_SET.txt'),'w') as f2:
    f1.write('@TIMESTAMP')
    f2.write('TIMESTAMP = @TIMESTAMP')
    for idx, field in field_df.iterrows():
        if any(substring in field.field_name for substring in ['IRE', 'ISP', '__FX__val']):
            continue
        sql = 'ALTER TABLE {} ADD COLUMN {} {};'.format(table_name, field.field_name, field.data_type)    
        cursor.execute(sql)    
        sql = 'ALTER TABLE {} MODIFY COLUMN {} {} COMMENT \'{}\';'.format(table_name, field.field_name, field.data_type, field.description)
        cursor.execute(sql)
        f1.write(',@{}'.format(field.field_name))
        f2.write(',{} = nullif(@{}, \'\')'.format(field.field_name, field.field_name))

