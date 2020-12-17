#!/usr/bin/python

####################################################

#FILE         : notify_json_v2.py 
#DESCRIPTION  : This script is a modification of the FastNetMon notify_json script that also updates an external google spreadsheet connecting to Klipfolio. 
#USAGE        : cat ban.json | python notify_json_v2.py ban 192.168.1.1

#AUTHOR       : LNC
#CONTACT      : lisa.cao@cybera.ca
#DATE CREATED : Dec 10, 2020
#LAST REVISION: --- 

#NOTES        : Requires a google credentials.json file to be placed in Users/<username>/.config/gspread/credentials.json and a fastnetmon generated JSON to be taken as argument. For first time setup you will need to create a google project and enable API access on it. See here for more details: https://gspread.readthedocs.io/en/latest/oauth2.html#oauth-client-id. You will then have to set your spreadsheet URL

####################################################

import sys
import logging
import json
import pprint
import pandas as pd
import gspread
from datetime import datetime

# logging config
logging.basicConfig(filename='/tmp/fastnetmon_notify_script.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
if len(sys.argv) != 3:
    logging.error("Please provide two arguments for script: action and IP address")
    sys.exit(1)
    
action = sys.argv[1] # can be ban, unban, partial_block
ip_address = sys.argv[2]
stdin_data = sys.stdin.read()

# read in json data
data = json.loads(stdin_data)
data = pd.json_normalize(data)

# logging entry
logging.info("Start for action %s and IP %s" % (action, ip_address))
logging.info("We got following details: " + stdin_data)
logging.info("Decoded details from JSON: " + pprint.pformat(data))
# You can use attack details in this form:
# logging.info("Attack direction: " + data['attack_details']['attack_direction'])

# create dataframe
ddos_df = []
ddos_df = data.append(ddos_df, ignore_index = True)
ddos_df.columns = ddos_df.columns.str.replace('attack_details.', "")
ddos_df.insert(0, "date", str(datetime.now()))

# drop extra data from partial ban files
if "flow_spec_rules" in ddos_df.columns: 
    ddos_df = ddos_df.drop("flow_spec_rules", 1)
ddos_entry = ddos_df.values.tolist()

# please ensure you have your credentials placed in Users/<username>/.config/gspread/credentials.json
gc = gspread.oauth()
googleurl = 'https://docs.google.com/spreadsheets/d/1bYvK9mYiHtFGRXhnOYsWO1eRVJWoDCrZjbyQSQEOATw/edit#gid=0'
spreadsheet = gc.open_by_url(googleurl)
worksheet = spreadsheet.sheet1

# set column names in spreadsheet
firstval = worksheet.acell('A1').value
if not firstval:
    colname_cells = worksheet.range('A1:AR1') # approximation 
    for i, val in enumerate(ddos_df.columns.values): 
        colname_cells[i].value = val
    worksheet.update_cells(colname_cells)

# find next empty row for append 
def next_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list) + 1)
next = next_row(worksheet)

# update spreadsheet values
cells = 'A{}'.format(next) + ':' + 'AR{}'.format(next)
cells = worksheet.range(cells)
cell_values = ddos_entry[0]

for i, val in enumerate(cell_values): 
    cells[i].value = val
worksheet.update_cells(cells)
