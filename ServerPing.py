import sys
import os
import time
import argparse
import logging
import threading
import subprocess
import platform


# SERVER PINGER ------------------------------------------------------------------- #
class server_pinger:
# ------------------------- #

    def __init__(self, name, logger, address, down_command, up_command, delay, error_delay, error_count, ping_send, ping_required):
        self.name = name
        self.logger = logger
        self.address = address
        self.down_command = down_command
        self.up_command = up_command
        self.delay = delay
        self.error_delay = error_delay
        self.error_count = error_count
        self.ping_send = ping_send
        self.ping_required = ping_required
        
        self.up_down = True
        self.starting = True

# ------------------------- #

    def start(self):
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.name = self.name
        self.thread.daemon = True
        self.thread.start()
        
# ------------------------- #

    def startup(self, up_down, packets_recieved, packets_sent, count=1):
        self.starting = False
        self.up_down = up_down
        if up_down:
            self.logger.info("Server started Online (" + str(packets_recieved) + "/" + str(packets_sent) + " packets)")
        else:
            self.logger.info("Server started Offline (" + str(count) + "/" + str(count) + " tries)")

# ------------------------- #

    def run_loop(self):
        self.logger.debug("Server Pinger running")
        while True:
            self.run_check()
            time.sleep(self.delay)
        
# ------------------------- #
     
    def run_check(self):
        try:
            output = self.ping(server=self.address, count=self.ping_send)
            received = output['received']
            ping_error_string = ''
        except:
            ping_error_string = "[Ping Error: " + str(output) + "]"
            received = 0
            
        if int(received) >= self.ping_required:
            if self.starting: # Check for first round
                self.startup(up_down=True, packets_recieved=received, packets_sent=self.ping_send)
                return

            self.logger.debug("Server replied to ping! (" + str(received) + "/" + str(self.ping_send) + " packets)")
            if not self.up_down: self.server_up()
            return
        else:
            self.logger.debug("Server DID NOT reply to ping! (" + str(received) + "/" + str(self.ping_send) + " packets) " + ping_error_string)
            if not self.up_down: return
            if self.error_count == 1:
                if self.starting: # Check for first round
                    self.startup(updown=False, packets_received=received, packets_sent=ping_send, count=1)
                    return
                self.server_down()
            else:
                self.error_recheck(1)
    
# ------------------------- #
    
    def error_recheck(self, count):
        time.sleep(self.error_delay)
        
        count += 1
        try:
            output = self.ping(server=self.address, count=self.ping_send)
            received = output['received']
            ping_error_string = ''
        except:
            ping_error_string = "[Ping Error: " + str(output) + "]"
            received = 0
        
        if int(received) >= self.ping_required:
            self.logger.debug("Ping reacquired after " + str(count) + " ping attempts!")
            return
        else:
            self.logger.debug("Server DID NOT reply to ping retry! (" + str(count) + "/" + str(self.error_count) + " tries) (" + str(received) + "/" + str(self.ping_send) + " packets) " + ping_error_string)
            if count >= self.error_count:
                if self.starting: # Check for first round
                    self.startup(updown=False, packets_received=received, packets_sent=ping_send, count=count)
                    return
                self.server_down()
                return
            else:
                # If not at max count, Recurse
                self.error_recheck(count)
                
# ------------------------- #

    def server_up(self):
        self.logger.info("Server has come back Online")
        output = os.system(self.up_command)
        self.logger.debug("Output of Up-Command: " + str(output))
        self.up_down = True
      
# ------------------------- #
        
    def server_down(self):
        self.logger.info("Server has gone offline")
        output = os.system(self.down_command)
        self.logger.debug("Output of Down-Command: " + str(output))
        self.up_down = False

# ------------------------- #
      
    def ping(self, server='example.com', count=1, wait_sec=1):
        cmd = "ping -{} {} {}".format('n' if platform.system().lower()=="windows" else 'c', count, server).split(' ')
        try:
            output = subprocess.check_output(cmd).decode().strip()
            lines = output.split("\n")
            
            if platform.system().lower()!="windows":
                loss = lines[-2].split(',')[2].split()[0]
                received = lines[-2].split(',')[1].split()[0]
            else:
                loss = lines[-3].split(',')[2].split()[3][1:]
                received = lines[-3].split(',')[1].split()[2]
                
            return {
                'lines': lines,
                'received': received,
                'loss': loss
            }

        except Exception as e:
            #self.logger.debug("Ping Exception: " + str(e))
            return e

# ------------------------------------------------------------------- SERVER PINGER #