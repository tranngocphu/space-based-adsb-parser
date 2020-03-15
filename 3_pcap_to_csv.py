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

    1. Parse pcap file to csv. During parsing, construct TIMESTAMP field as follows.
        TIMESTAMP format: YYYY-MM-DD HH:MM:SS   
            Dates are extracted from pcap file names given by ANSP
            Times are the same with time_reception_of_position in the data
"""



import os

from helpers import pcap_to_csv, get_field_from_pcap, get_file_list_in_dir, get_field_list_from_csv
from constants import ADSB_PENDING_PATH, CSV_PATH, FIELD_PATH


# PCAP files
pending_file = get_file_list_in_dir(ADSB_PENDING_PATH)

# get field list from csv
field_csv_file = os.path.join(FIELD_PATH, 'asterix_cat021_2_4_dtype.csv')
field_list, _ = get_field_list_from_csv(field_csv_file)

field_list_final = []

for item in field_list:
    if any(substring in item for substring in ['IRE', 'ISP', '__FX__val']):
        continue
    field_list_final.append(item)

field_list_final.sort()    

for pcap_file in pending_file:    
    pcap_to_csv(pcap_file, field_list_final, CSV_PATH)
