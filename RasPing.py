##!/usr/bin/python3

import sys
import os
import time
import signal
import logging
import argparse
import configparser
import threading
import platform
import urllib.request
from logging.handlers import RotatingFileHandler

from ServerPing import server_pinger
from WebsitePing import web_pinger

# LOGGING SETUP --------------------------------- #
logger_boy = logging.getLogger('RasPing')
logger_boy.setLevel(logging.DEBUG)

formatstr = '%(asctime)s - %(threadName)15s - %(levelname)7s - %(message)s'
formatter = logging.Formatter(formatstr)

fh = RotatingFileHandler('logs/RasPing.log', maxBytes=2000000, backupCount=2)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger_boy.addHandler(fh)
logger_boy.addHandler(ch)
# --------------------------------- LOGGING SETUP #

# OBJECT ARRAYS --------------------------------- #
Server_Objects = []
Webpage_Objects = []
# --------------------------------- OBJECT ARRAYS #

def run():
    logger_boy.info('###########################################')
    logger_boy.info("Service started!")
    
    for Server in Server_Objects:
        Server.start()

    for Webpage in Webpage_Objects:
        Webpage.start()

    while True:
        time.sleep(1000)
        pass
    
def parse_config_file(config_file):
    
    cajigerator = configparser.ConfigParser(allow_no_value=True)
    cajigerator.read(config_file)
    
    for object in cajigerator.sections():
        name = str(object)
        dict = cajigerator[object]
        if ('Server' in dict) and (not('Webpage' in dict)):
            Server_Objects.append(server_pinger(
                name = name,
                logger=         logger_boy,
                address=        dict.get('address'),
                down_command=   dict.get('down_command'),
                up_command=     dict.get('up_command'),
                delay=          time_parser(dict.get('delay')),
                error_delay=    time_parser(dict.get('retry_delay')),
                error_count=    int(dict.get('retry_count')) + 1,
                ping_send=      int(dict.get('packets_per_ping')),
                ping_required=  int(dict.get('packets_required'))
            ))
        elif (not ('Server' in dict)) and ('Webpage' in dict):
            Webpage_Objects.append(web_pinger(
                name = name,
                logger=         logger_boy,
                address=        dict.get('address'),
                down_command=   dict.get('down_command'),
                up_command=     dict.get('up_command'),
                delay=          time_parser(dict.get('delay')),
                error_delay=    time_parser(dict.get('retry_delay')),
                error_count=    int(dict.get('retry_count')) + 1
            ))
        else:
            raise ("Error: Must Specify 'Server' or 'Webpage' in config file (not both)")
        
def time_parser(time_string):
    if ('sec' in time_string) and (not('min' in time_string)):
        time_string = time_string.replace('sec', '')
        return int(time_string)
    elif (not('sec' in time_string)) and ('min' in time_string):
        time_string = time_string.replace('min', '')
        return (60 * int(time_string))
    elif (not('sec' in time_string)) and (not('min' in time_string)):
        return (60 * int(time_string))
    else:
        raise ("Error: Cannot use both 'min' and 'sec' in delay definition in config file")
    

    
# --------------------------------------------------------------------------------- #

if __name__ == "__main__":
    parse_config_file("RasPing.conf")
    run()
    
