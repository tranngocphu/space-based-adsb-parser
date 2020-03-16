"""
This script is indenpendent of the parser codes.
Created by Phu N. Tran on 16 March 2020.
Contact: phutran@ntu.edu.sg
"""

import pymysql
import pandas as pd
import time

HOST = ''
PORT =  ''
USER = ''
PASSWORD = ''
DATABASE = ''


def create_sql_connection():
    try:
        sql_con = pymysql.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            db=DATABASE,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Successfully connected to the database {} in host {}.".format(DATABASE, HOST))
        return sql_con
    except pymysql.err.OperationalError as err:
        print(err.args[1])
        return False

sql_con = create_sql_connection() 

# query all columns where Callsign is not NULL, limit to 10000 rows
sql = 'SELECT * FROM ORIGINAL_DATA WHERE I170__TId__val IS NOT NULL LIMIT 10000;'
start = time.time()
df = pd.read_sql(sql, sql_con)  # store query result in the pandas dataframe
duration = time.time() - start
print(duration)
