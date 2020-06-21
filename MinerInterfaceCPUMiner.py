# Miner Interface Class to:
#   handle comms with cpuminer
#   translate from cpuminer to the format required by MinerInterfaceAbstract

from apscheduler.schedulers.background import BackgroundScheduler
from .HashRateUnitsEnum import HashRateUnits
from .MinerInterfaceAbstract import MinerInterfaceAbstract
import socket
import json
import time


class MinerInterface(MinerInterfaceAbstract):

    def __start_connection(self, host, port):
        addr = (host, port)
        #print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setblocking(False)
        sock.connect_ex(addr)
        return sock

    def __split_groups(self, input_string):
        split_str = input_string.split('=')
        return split_str

    def __refresh_data_from_miner(self):
        try:
            sock = self.__start_connection(self.__miner_ip, self.__miner_port)
            #print("sending summary")
            sock.sendall('summary'.encode('utf-8'))
            data = sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        except BrokenPipeError:
            self.__miner_connected = False
            print(
                'No link to cpuminer available - check it is running and has API configured')
        else:
            if data:
                # Need to trim the extra char off the end
                decoded_data = (data.decode('utf-8'))[:-2]
                data_dic = dict(
                    map(self.__split_groups, decoded_data.split(";")))
                # Got all the data now put it in the interface's properties
                self.__threads = data_dic['CPUS']
                self.__hash_rate = data_dic['KHS']
                self.__hash_rate_units = HashRateUnits.KH_S
                self.__block_found = data_dic['SOLV']
                self.__cpu_freq = {'CPU1': data_dic['FREQ']}
                self.__uptime = time.strftime(
                    "%H:%M:%S", time.gmtime(int(data_dic['UPTIME'])))
                self.__miner_name = data_dic['NAME'] + ' - ' + data_dic['VER']
                self.__miner_connected = True
                self.__miner_has_been_connected = True
            else:
                self.__miner_connected = False
                raise RuntimeError("Peer closed.")

    def __init__(self, refresh_interval, local_miner_API_ip, local_miner_API_port):
        self.__threads = -1
        self.__hash_rate = -1
        self.__hash_rate_units = HashRateUnits.UNKNOWN
        self.__block_found = -1
        self.__cpu_freq = {'NONE': -1}
        self.__uptime = "00:00:00"
        self.__miner_name = "CPUMINER"
        self.__miner_connected = False
        self.__miner_has_been_connected = False
        self.__refresh_interval_seconds = refresh_interval

        self.__miner_ip = local_miner_API_ip
        self.__miner_port = local_miner_API_port

        # setup a scheduler to refresh data from the miner
        self.__scheduler = BackgroundScheduler()
        self.__scheduler.add_job(self.__refresh_data_from_miner,
                                 'interval', seconds=self.__refresh_interval_seconds)
        self.__scheduler.start()

        # get an inital data set from the miner
        self.__refresh_data_from_miner()

    def __del__(self):
        # stop the scheduler on shutdown
        self.__scheduler.shutdown()

    @property
    def threads(self) -> int:
        return self.__threads

    @property
    def hash_rate(self) -> int:
        return self.__hash_rate

    @property
    def hash_rate_units(self) -> HashRateUnits:
        return self.__hash_rate_units

    @property
    def blocks_found(self) -> int:
        return self.__block_found

    @property
    def cpu_freq(self) -> dict:
        return self.__cpu_freq

    @property
    def uptime(self) -> str:
        return self.__uptime

    @property
    def miner_name(self) -> str:
        return self.__miner_name

    @property
    def miner_connected(self) -> bool:
        return self.__miner_connected

    @property
    def miner_has_been_connected(self) -> bool:
        return self.__miner_has_been_connected

    @miner_has_been_connected.setter
    def miner_has_been_connected(self, state):
        self.__miner_has_been_connected = state

    @property
    def refresh_interval_seconds(self) -> int:
        return self.__refresh_interval_seconds
