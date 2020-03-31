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

# csv files
csv_files = get_file_list_in_dir(CSV_PATH)

for i in range(0, len(csv_files)):
    csv_file = csv_files[i]
    
    f = open(csv_file, 'rt')
    header = f.readline().replace('\n','')    
    f.close()  
    header = header.split(',')
    cols = ['@{}'.format(col) for col in header]
    cols_order = ','.join(cols)

    cols_set = ['{}=nullif(@{},\'\')'.format(col,col) for col in header ] 
    cols_set = ','.join(cols_set)   
    
    
    file_name = os.path.basename(csv_file)
    file_name = file_name.split('_')[2]
    year = file_name[0:4]
    month = file_name[4:6]
    table_name = 'TRACKS_{}_{}'.format(year,month)
    
    sql = """LOAD DATA LOCAL INFILE '{}' IGNORE
            INTO TABLE {} 
            FIELDS TERMINATED BY ','
            LINES TERMINATED BY '\\n'
            IGNORE 1 LINES
            ({}) SET {};""".format(csv_file, table_name, cols_order, cols_set)

    print(csv_file, '-->', table_name)
    before = time.datetime.now()
    result = cursor.execute(sql)
    after = time.datetime.now()
    print(i, after - before, '\n')