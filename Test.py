#!/usr/bin/python3

import logging
import subprocess
import platform
import time
from ServerPing import server_pinger



logger_boy = logging.getLogger('RasPing')
logger_boy.setLevel(logging.DEBUG)

formatstr = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(formatstr)

fh = logging.FileHandler('log.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger_boy.addHandler(fh)
logger_boy.addHandler(ch)


test_object = server_pinger(
    name = 'RasNas Server',
    logger = logger_boy,
    address = '10.0.1.175',
    down_command = "start notepad++.exe",
    up_command = "start notepad.exe",
    delay = 30,
    error_delay = 10,
    error_count = 1,
    ping_send = 3,
    ping_required = 2
)


while True:
    time.sleep(10)
    pass