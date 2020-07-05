# Portions of this code have been derived from https://realpython.com/python-sockets which has the following license:

# MIT License

# Copyright (c) 2018 Real Python

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# The remainder of the code has been developed by Neil Birtles

import selectors
import socket
import sys
import traceback
import argparse

from apscheduler.schedulers.background import BackgroundScheduler

from MinerInfoLocalClientMessageLib import Client_Message_Handler
from MinerInterfaceCPUMiner import MinerInterface

# default ips and ports 
controller_ip = '10.0.0.250'
controller_port = 55440
local_miner_API_ip = "127.0.0.1"
local_miner_API_port = 4048

# get and send miner info every second
refresh_interval_seconds = 5

def create_message(miner_info):
    return dict(
        type="text/json",
        encoding="utf-8",
        content=miner_info
    )


def start_connection():
    if miner_interface.miner_connected or miner_interface.miner_has_been_connected:
        if miner_interface.miner_connected:
            miner_info = create_message({
                    'threads': miner_interface.threads,
                    'hashrate': miner_interface.hash_rate,
                    'hashrate_units': int(miner_interface.hash_rate_units),
                    'blocks_found': miner_interface.blocks_found,
                    'cpu_freq': miner_interface.cpu_freq,
                    'uptime': miner_interface.uptime,
                    'miner_type': miner_interface.miner_name,
                    'miner_connected': miner_interface.miner_connected
                })
        else:
            #if the miner has been connected once then send a notice that its now disconnected
            miner_interface.miner_has_been_connected = False
            miner_info = create_message({
                    'threads': 0,
                    'hashrate': 0,
                    'hashrate_units': 0,
                    #keep the number of blocks found as still valid historical info 
                    'blocks_found': miner_interface.blocks_found,
                    'cpu_freq': { 'NONE' : -1 },
                    'uptime': "00:00:00",
                    'miner_type': "unknown",
                    'miner_connected': False
                })

        addr = (controller_ip, controller_port)
        print("\n ---------------------- \nstarting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_WRITE 
        # selectors.EVENT_READ |
        message = Client_Message_Handler(sel, sock, addr, miner_info)
        sel.register(sock, events, data=message)


# Initiate the argument parser
arg_parser = argparse.ArgumentParser(description="Standardised interface for crypto miners to the SBC Miner")
arg_parser.add_argument("-L", "--localip", help="IP address for the local miner", default=local_miner_API_ip)
arg_parser.add_argument("-l", "--localport", help="API port number for the local miner", default=local_miner_API_port)
arg_parser.add_argument("-s", "--sbcminerip", help="IP address for the SBC Miner", default=controller_ip)
arg_parser.add_argument("-S", "--sbcminerport", help="Miner Info port number for the SBC Miner", default=controller_port)
# parse and save the command line arguments 
arguments = arg_parser.parse_args()
controller_ip = arguments.sbcminerip
controller_port = arguments.sbcminerport
local_miner_API_ip = arguments.localip
local_miner_API_port = arguments.localport


#start the miner interface 
miner_interface = MinerInterface(refresh_interval_seconds, local_miner_API_ip, local_miner_API_port)

sel = selectors.DefaultSelector()

#setup a scheduler to send updates
scheduler = BackgroundScheduler()
scheduler.add_job(start_connection, 'interval', seconds=refresh_interval_seconds)
scheduler.start()

try:    
    #do an initial push of info
    start_connection()

    while True:
        events = sel.select(timeout=refresh_interval_seconds)
        for key, mask in events:
            message_handler = key.data
            try:
                message_handler.process_events(mask)
            except Exception as e:
                print(
                    "main: error: exception for",
                    f"{message_handler.addr}:{e}",
                )
                message_handler.close()
        # Check for a socket being monitored to continue - dont want to do this - run until keyboard exit
        # if not sel.get_map():
        #     # message has been sent so break out of inner loop to get a new refresh
        #     break
    #while True

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
