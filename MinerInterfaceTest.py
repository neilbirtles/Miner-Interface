from time import sleep
from MinerInterfaceCPUMiner import MinerInterface

test = MinerInterface(2)

while True:
    sleep(1)
    print(test.hash_rate)
    print(test.hash_rate_units)
    print(test.miner_connected)
    print(test.miner_name)
    print(test.refresh_interval_seconds)
    print(test.threads)
    print(test.uptime)
    
    