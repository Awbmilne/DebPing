import sys
import os
import time
import argparse
import logging
import threading
import subprocess
import platform
import urllib.request

# WEB PINGER ------------------------------------------------------------------- #
class web_pinger:
# ------------------------- #

    def __init__(self, name, logger, address, down_command, up_command, delay, error_delay, error_count):
        self.name = name
        self.logger = logger
        self.address = address
        self.down_command = down_command
        self.up_command = up_command
        self.delay = delay
        self.error_delay = error_delay
        self.error_count = error_count
        
        self.up_down = True
        self.starting = True

# ------------------------- #

    def start(self):
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.name = self.name
        self.thread.daemon = True
        self.thread.start()
        
# ------------------------- #

    def startup(self, up_down, count=1):
        self.starting = False
        self.up_down = up_down
        if up_down:
            self.logger.info("Webpage started Online")
        else:
            self.logger.info("Webpage started Offline (" + str(count) + "/" + str(count) + " tries)")

# ------------------------- #

    def run_loop(self):
        self.logger.debug("Webpage Pinger running")
        while True:
            self.run_check()
            time.sleep(self.delay)
        
# ------------------------- #
     
    def run_check(self):
        try:
            code = self.check_page()
        except:
            code = "N/A"
            
        if code == 200:
            if self.starting: # Check for first round
                self.startup(up_down=True)
                return

            self.logger.debug("Webpage replied to ping!")
            if not self.up_down: self.server_up()
            return
        else:
            self.logger.debug("Webpage DID NOT reply with 200! (HTTP-Code: " + code + ")")
            if not self.up_down: return
            if self.error_count == 1:
                if self.starting: # Check for first round
                    self.startup(updown=False, count=1)
                    return
                self.server_down()
            else:
                self.error_recheck(1)
    
# ------------------------- #
    
    def error_recheck(self, count):
        time.sleep(self.error_delay)
        
        count += 1
        try:
            code = self.check_page()
        except:
            code = "N/A"
        
        if code == 200:
            self.logger.debug("Webpage reacquired after " + str(count) + " attempts!")
            return
        else:
            self.logger.debug("Webpage DID NOT reply with 200 to retry! (" + str(count) + "/" + str(self.error_count) + " tries)")
            if count >= self.error_count:
                if self.starting: # Check for first round
                    self.startup(updown=False, count=count)
                    return
                self.server_down()
                return
            else:
                # If not at max count, Recurse
                self.error_recheck(count)
                
# ------------------------- #

    def server_up(self):
        self.logger.info("Webpage has come back Online")
        output = os.system(self.up_command)
        self.logger.debug("Output of Up-Command: " + str(output))
        self.up_down = True
      
# ------------------------- #
        
    def server_down(self):
        self.logger.info("Webpage has gone offline")
        output = os.system(self.down_command)
        self.logger.debug("Output of Down-Command: " + str(output))
        self.up_down = False

# ------------------------- #
      
    def check_page(self):
        return urllib.request.urlopen(self.address).getcode()

# ------------------------------------------------------------------- WEB PINGER #