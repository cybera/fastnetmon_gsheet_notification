#!/usr/bin/python

import json
import gspread
import os
import pprint
import sys
import syslog

from datetime import datetime

syslog.openlog("fnm_notify_json_v2")
syslog.syslog(syslog.LOG_ALERT, 'notify_json_v2 starting')


def next_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list) + 1)


DEBUG = False
if os.getenv('FNM_DEBUG', False) is not False:
    DEBUG = True

config_file = '/tmp/fnm_google_notify.json'
home = os.getenv('HOME')
if home is not None:
    config_file = "%s/.fnm_google_notify.json" % (home)

try:
    with open(config_file) as j:
        config = json.load(j)
except Exception as e:
    syslog.syslog(syslog.LOG_ERR, "Unable to read %s: %s" % (config_file, e))

# can be ban, unban, partial_block
action = sys.argv[1]
ip_address = sys.argv[2]
stdin_data = sys.stdin.read()

# read in json data
data = json.loads(stdin_data)

# logging entry
if DEBUG:
    syslog.syslog("Start for action %s and IP %s" % (action, ip_address))
    syslog.syslog("We got following details: " + stdin_data)
    syslog.syslog("Decoded details from JSON: " + pprint.pformat(data))
    # You can use attack details in this form:
    # logging.info("Attack direction: " + data['attack_details']['attack_direction'])

report = {}
report['basic'] = {}
report['basic']['ip'] = data['ip']
report['basic']['action'] = data['action']
report['basic']['date'] = str(datetime.now())


report['attack_details'] = {}
if 'attack_details' in data:
    for k, v in data['attack_details'].items():
        if type(v) == list:
            values = ','.join(str(v) for v in v)
        else:
            v = str(v)
        report['attack_details'][k] = v

report['flow_spec_rules'] = {}
if 'flow_spec_rules' in data:
    idx = 1
    for i in data['flow_spec_rules']:
        for k, v in i.items():
            prefix = "flow_spec_rules-%s-%s" % (idx, k)
            if type(v) == list:
                v = ','.join(str(v) for v in v)
            else:
                v = str(v)
            report['flow_spec_rules'][prefix] = v
        idx += 1

# please ensure you have your credentials placed in Users/<username>/.config/gspread/credentials.json
gc = gspread.service_account(filename=config_file)
googleurl = config['sheet_url']
spreadsheet = gc.open_by_url(googleurl)
worksheet = spreadsheet.sheet1

# set column names in spreadsheet
if worksheet.acell('A1').value != 'Date':
    worksheet.update('A1', 'Date')

if worksheet.acell('B1').value != 'Action':
    worksheet.update('B1', 'Action')

if worksheet.acell('C1').value != 'IP':
    worksheet.update('C1', 'IP')

idx = 0
colname_cells = worksheet.range('D1:ZR1')
for k in sorted(report['attack_details'].keys()):
    if colname_cells[idx].value != k:
        colname_cells[idx].value = k
    idx += 1

for k in sorted(report['flow_spec_rules'].keys()):
    if colname_cells[idx].value != k:
        colname_cells[idx].value = k
    idx += 1

worksheet.update_cells(colname_cells)

next = next_row(worksheet)

# update spreadsheet values
cells = 'A{}'.format(next) + ':' + 'ZR{}'.format(next)
cells = worksheet.range(cells)

cells[0].value = report['basic']['date']
cells[1].value = report['basic']['action']
cells[2].value = report['basic']['ip']

idx = 3

for k in sorted(report['attack_details'].keys()):
    cells[idx].value = report['attack_details'][k]
    idx += 1

for k in sorted(report['flow_spec_rules'].keys()):
    cells[idx].value = report['flow_spec_rules'][k]
    idx += 1

worksheet.update_cells(cells)
