"""
PCAP ADSB DATA PARSER FOR SQL SERVER

Date: 13 March 2020
Author: Phu Tran
Affiliation: 
    Air Traffic Management Research Institute
    Nanyang Technological Univerity
    Singapore
Email: phutran@ntu.edu.sg

THIS SCRIPT PERFORMS:

    1. Load csv files to sql table
"""



import os
import pymysql
import datetime as time
from helpers import get_file_list_in_dir
from constants import ADSB_PENDING_PATH, CSV_PATH, FIELD_PATH
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

# PCAP files
csv_files = get_file_list_in_dir(CSV_PATH)

with open(os.path.join(FIELD_PATH, 'field_list_sql.txt'), 'r') as f:
    field_list = f.readline()

with open(os.path.join(FIELD_PATH, 'field_list_sql_SET.txt'), 'r') as f:
    field_list_SET = f.readline()

print(field_list)

for i in range(0, len(csv_files)):
    csv_file = csv_files[i]
    sql = """LOAD DATA LOCAL INFILE '{}' IGNORE
            INTO TABLE {} 
            FIELDS TERMINATED BY ','
            LINES TERMINATED BY '\\n'
            IGNORE 1 LINES
            ({}) SET {};""".format(csv_file, table_name, field_list, field_list_SET)

    print(csv_file)
    before = time.datetime.now()
    result = cursor.execute(sql)
    after = time.datetime.now()
    print(i, after - before, '\n')

