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

    1. Parse the Cat 021 Data XML file to csv. 
        Output is all data field names, for example:            
            I008__ARV__val,
            I008__CDTI_A__val,
            I090__GVA__val,
            I090__NACp__val,                       
"""

import os
import json
import xmltodict
import csv

from constants import FIELD_PATH



def read_fixed(data_format, is_compound=False):
    result = []
    if 'Fixed' not in data_format.keys():
        return []
    fixeds = data_format['Fixed']
    if isinstance(fixeds, dict):
        fixeds = [fixeds]
    for fixed in fixeds:
        fields = fixed['Bits']
        if isinstance(fields, dict):
            fields = [fields]
        for field in fields:
            name = ''
            meaning = ''
            short_name = field["BitsShortName"]
            if 'BitsName' in field.keys():
                name = field['BitsName'] 
            if 'BitsValue' in field.keys():
                meaning = json.loads(json.dumps(field['BitsValue']))
            if not is_compound:
                field_name = "I{}__{}__val".format(item_id,short_name)
            else:
                field_name = "I{}__{}__{}__val".format(item_id,short_name,short_name)
            result.append({
                'field_name': field_name,
                'description': name,
                'meaning': meaning
            })       
    return result


def read_variable(data_format, is_compound=False):
    result = []
    variables = data_format['Variable']
    if isinstance(variables, dict):
        variables = [variables]
    for variable in variables:
        result = result + read_fixed(variable, is_compound)
    return result


def read_repetitive(data_format, is_compound=False):
    result = []
    repetitives = data_format['Repetitive']
    if isinstance(repetitives, dict):
        repetitives = [repetitives]
    for repetitive in repetitives:
        result = result + read_fixed(repetitive, is_compound)
    return result


def read_compound(data_format, is_compound=False):
    result_variable = []
    result_repetitive = []
    compounds = data_format['Compound']
    if isinstance(compounds, dict):
        compounds = [compounds]
    for compound in compounds:
        if 'Variable' in compound.keys():                        
            result_variable = result_variable + read_variable(compound, is_compound)
        if 'Repetitive' in compound.keys():
            result_repetitive = result_repetitive + read_repetitive(compound, is_compound)
    return result_variable + result_repetitive


def read_explicit(data_format):
    result = []
    explicits = data_format['Explicit']
    if isinstance(explicits, dict):
        explicits = [explicits]
    for explicit in explicits:
        if 'Fixed' in explicit.keys():            
            result = result + read_fixed(explicit)
        elif 'Variable' in explicit.keys():
            result = result + read_variable(explicit)
        elif 'Compound' in explicit.keys():
            result = result + read_compound(explicit)
    return result



if __name__ == "__main__":    
    
    dtype_file = os.path.join(FIELD_PATH,'all_val_field_dtype.csv')    
    
    ## DATA CAT SELECTION
    
    data_cat = 'adsb'
    # data_cat = 'asmgcs'

    if data_cat == 'adsb':
        xml_file = os.path.join(FIELD_PATH,'asterix_cat021_2_4.xml')
        csv_file = os.path.join(FIELD_PATH,'asterix_cat021_2_4.csv')
        txt_file = os.path.join(FIELD_PATH,'asterix_cat021_2_4.txt')
    else :
        xml_file = os.path.join(FIELD_PATH,'asterix_cat062_1_17.xml')
        csv_file = os.path.join(FIELD_PATH,'asterix_cat062_1_17.csv')
        txt_file = os.path.join(FIELD_PATH,'asterix_cat062_1_17.txt')

    
    # READ EXISTING DATA TYPES

    with open(dtype_file, mode='r') as infile:
        reader = csv.reader(infile)
        dtype = {rows[0]:rows[1] for rows in reader}
    
    
    # READ XML FILE (STRUTURE OF DATA)
         
    with open(xml_file) as in_file:
        xml = in_file.read()    
        result = xmltodict.parse(xml)


    # PARSE XML

    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['field_name', 'data_type'])

        items = result['Category']['DataItem']
        result = []

        for item in items:                
            item_id = item['@id']
            data_format = item['DataItemFormat']
            if 'Fixed' in data_format.keys():            
                result = result + read_fixed(data_format)        
            elif 'Variable' in data_format.keys():                        
                result = result + read_variable(data_format)
            elif 'Repetitive' in data_format.keys():                        
                result = result + read_repetitive(data_format)
            elif 'Compound' in data_format.keys():            
                result = result + read_compound(data_format)
            elif 'Explicit' in data_format.keys():
                result = result + read_explicit(data_format)
            else:
                print("==={}====NO KEY FOUND=======",format(item_id))
                

    with open(txt_file, 'w') as filehandle:
        for item in result:
            filehandle.write('{}\n'.format(item))

    
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['field_name', 'data_type', 'description'])
        for field in result:
            if 'spare' in field['field_name']:
                continue
            field_name = field['field_name']
            description = field['description']
            try:
                data_type = dtype[field['field_name']]
            except KeyError:
                data_type = ''
            writer.writerow([field_name, data_type, description])
