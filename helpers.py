import asterix
import dpkt
from functools import reduce
import operator
import csv
import os
import json
import pandas as pd
import time

from constants import I021_SQL_TABLE_NAME, I021_DATA_DICT



def list_to_txt(list_, txt_file):
    file = open(txt_file, 'w')    
    for i in range(0, len(list_)):
        file.write(list_[i])
        file.write('\n')


def clean_key_path(path, sep='__'):
    keys = path.split('__')
    n = len(keys)
    if n==1:
        return path   
    assert(keys[-1] in ['val', 'desc', 'meaning', 'max', 'min', 'const']) 
    second_last = keys[n-2]
    third_last = keys[n-3]    
    if second_last==third_last:
        find = sep + third_last + sep + second_last        
        replace = sep + third_last
        path = path.replace(find, replace)
        assert(keys[0] in ['I110','I220','I295','IRE','RE'])
    return path



def get_file_list_in_dir(dir):
    """Function to get list of all files in a
    given folder and its subfolders. Files list
    is sorted alphabetically. 
    """
    all_files = []
    for subdir, dirs, files in os.walk(dir):
        for file in files:            
            all_files.append(subdir + os.sep + file)
    all_files.sort()
    return all_files



def get_date_from_file_path(file_path):
    """Extract date from pcap file name.
    File name should look like, for examples:
        11.138.6_00001_20200228115536.113_1Hrs   
        11.138.6_00001_20200228115536.113_1Hrs
        11.138.6_00001_20200228115536.113_1Hrs
    Argument:
        File name as above
    Returns:
        Full date in YYYYMMDD
    """
    file_name = os.path.basename(file_path)
    elements = file_name.split('_')
    datestring = elements[2]
    return '{}-{}-{}'.format(datestring[0:4], datestring[4:6], datestring[6:8])



def get_timestamp(date, time_in_sec):
    time_hhmmss = time.strftime('%H:%M:%S', time.gmtime(time_in_sec))
    return '{} {}'.format(date, time_hhmmss)



def get_from_dict(data_dict, chained_key):
    """Function to access dictionary value by list of chained keys"""
    return reduce(operator.getitem, chained_key, data_dict)



def get_chained_key(d, current = []):
    """Recursively get all possible key paths
    in a given dictionary    
    """
    for a, b in d.items():        
        if isinstance(b, dict):
            yield from get_chained_key(b, current+[a])
        ## uncomment below if there is list in the dictionary
        # elif isinstance(b, list):
        #     for i in b:
        #         yield from get_paths(i, current+[a])
        else:
            yield current+[a]



def get_sample_dict_pcap(pcap_file, txt_file):
    """Show a sample of dictionay from pcap"""
    with open(pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        
        for _, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            data = eth.ip.udp.data

            # Parse data
            parsed = asterix.parse(data)             

            n = min(len(parsed),10)
            sample = parsed[0:n]     
            # print(sample)

            with open(txt_file, 'w') as file:
                file.write(json.dumps(sample))
            
            break



def get_field_from_pcap(pcap_file, field_sep='__'):
    """Get all possible data fields from a raw data file.
    Data fields returned as chained keys (from raw dictionary)
    """

    with open(pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)

        val_fields = []
        meta_fields = []
        all_fields = []

        cntr = 0

        print("Start processing file {}".format(pcap_file))

        for _, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            data = eth.ip.udp.data

            print('Pcap2Field {}: parsing packet {}'.format(pcap_file,cntr))
            cntr += 1

            # Parse data
            parsed = asterix.parse(data)

            for item in parsed:
            
                # Get keys path
                paths = list(get_chained_key(item))   # return a list         

                for path in paths:                
                    path = field_sep.join(path)   # return a string                   
                    path = clean_key_path(path)   # remove duplicate from compound items  
                    if path not in all_fields:
                        all_fields.append(path)                  
                    if ((field_sep + 'val') in path or path in ['category', 'len', 'crc', 'ts']):                        
                        # check if this field is value, not description
                        if path not in val_fields:
                            val_fields.append(path)
                    else:                
                        if path not in meta_fields:
                            meta_fields.append(path)  
    
    val_fields.sort()
    meta_fields.sort()
    all_fields.sort()

    return all_fields, val_fields, meta_fields



def pcap_to_csv(pcap_file, field_list, csv_dir, key_sep='__'):
    """Parse a pcap file to a csv file"""

    file_name = os.path.basename(pcap_file)
    date = get_date_from_file_path(pcap_file)

    with open(pcap_file, 'rb') as pcapfile, open(os.path.join(csv_dir, file_name+'.csv'), 'w', newline='') as csvfile: 

        print("Start reading file {}".format(pcap_file))
        pcap = dpkt.pcap.Reader(pcapfile)                
        cntr = 0 

        writer = csv.writer(csvfile, delimiter=',') 

        # write header name line
        csv_field_list = ['TIMESTAMP'] + field_list
        writer.writerow(csv_field_list)
    
        for _, buf in pcap:                   
            print('Pcap2Csv {}: parsing packet {}'.format(pcap_file, cntr))
            cntr += 1
            eth = dpkt.ethernet.Ethernet(buf)
            data = eth.ip.udp.data
            # Parse data
            parsed = asterix.parse(data)

            for item in parsed:
                data_row = []  # empty data row
                time_field = 'I073__time_reception_position__val'
                time_chained_key = time_field.split(key_sep) 
                time_in_sec = get_from_dict(item, time_chained_key)
                timestamp = get_timestamp(date, time_in_sec)
                data_row.append(timestamp)

                for i in range(0, len(field_list)):  # field_list doesn't have TIMESTAMP field
                    chained_key = field_list[i].split(key_sep)  # convert field name to array of keys
                    try:
                        val = get_from_dict(item, chained_key)
                        data_row.append(val)
                    except KeyError: # field not found in item, write empty string to csv at this position
                        data_row.append('')                    

                # make sure the length od data lines always equal length of header line                               
                assert(len(data_row)==len(csv_field_list))                  
                writer.writerow(data_row)



def get_field_list_from_csv(csv_file):
    """Get list of all possible fields
    from a pre-made csv file.
    """
    df = pd.read_csv(csv_file)
    return list(df.field_name.values), df



def get_table_name_by_prefix(prefix):
    """Get the full table name that contains given prefix.
    Arguments:        
        prefix: the predix as string to search for the full name
    Returns:
        A full table name
    """
    try:
        return '{}_{}'.format(prefix, I021_DATA_DICT[prefix])
    except KeyError:
        return False




if __name__ == "__main__":
    filepath = '/home/production/DATA/Space Based ADS-B/pending/Space Based ADS-B Part 4 - 29 Feb 2020/11.138.6_00026_20200229120000.113_1Hrs'
    date = get_date_from_file_path(filepath)
    timestamp = get_timestamp(date, 40000)
    print(timestamp)

    