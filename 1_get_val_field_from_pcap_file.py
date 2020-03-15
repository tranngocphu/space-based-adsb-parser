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

    1. Extract all data fields ('val') existed in each pcap file. 
        Save these fields in text files for further process.
        Note: 
            1a) Decoded data from pcap is in dictionary format. For example:
            {
                "I008" : {
                    "RA": {
                        "val": "RA value",
                        "meaning": ''
                    }
                },
                "I295": {
                    "TID": {
                        "TID: {
                            "val" : "some value",
                            "meaning" : "some meaning"
                        }
                    }
                }
            }
            From these dictionaries, data field names are constructed as the combination of
            all keys in the dictionaries, separated by double underscore '__', and all
            duplications are removed (see 1b below). In above example dictionaries, data
            field names are: 'I008__RA__val', 'I295__TID__val'
            
            1b) For compound data item (defined in Eurocontrol Cat 021 Docs),
            data fields are repeated 2 times. These duplications are removed.
            For example: "I295__TID__TID__val" becomes "I295__TID__val"

    2. Compare the fields extracted from pcap files to the fields parsed from standard EUCONTROL's XML file.
        All files extracted from pcap files MUST appeart in the standard fields list.
   
"""

import os
import pandas as pd
from constants import ADSB_PENDING_PATH, FIELD_PATH
from helpers import get_file_list_in_dir, get_sample_dict_pcap, get_field_from_pcap, list_to_txt



"""Load standard fields, which came from the XML file"""

standard_field = pd.read_csv(os.path.join(FIELD_PATH,'asterix_cat021_2_4.csv'))
standard_field = list(standard_field.field_name.values)
standard_field.sort()


"""All files to be checked"""
files = get_file_list_in_dir(ADSB_PENDING_PATH)


"""
If fields already read, set below to False; otherwise set to True.
For newly received pcap files, this is normally True.
"""
READ_FIELD_FROM_PCAP = False


"""Read pcap files and create txt files of field names"""
if READ_FIELD_FROM_PCAP:
    for file_ in files:    
        _, val, _ = get_field_from_pcap(file_)
        field_file = os.path.join(FIELD_PATH, 'from_pcap', os.path.basename(file_))
        list_to_txt(val, field_file)    


"""All text filed creared in the previous step:"""
text_field_files = get_file_list_in_dir(os.path.join(FIELD_PATH, 'from_pcap'))


"""Don't check if field name include these substrings:"""
exclude_substring = ['spare', 'IRE', 'crc', 'category', 'len', 'ts']


"""Check if all field names appear in the standard field names"""
cntr = 0
for file_ in text_field_files:
    with open(file_) as f:
        fields = f.read().splitlines()
        for field in fields:        
            if any(substring in field for substring in exclude_substring):
                continue
            if field not in standard_field:
                cntr+=1  
                print('{}  ---{}'.format(field,os.path.basename(file_)))
                print('\n')        
if cntr==0:
    print('All fields are in standard fields.')