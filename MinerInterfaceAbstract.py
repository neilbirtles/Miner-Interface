# Abstract class for the Miner Interface - all miner interfaces must subclass this

from abc import ABC,abstractmethod 
from HashRateUnitsEnum import HashRateUnits

class MinerInterfaceAbstract(ABC):
    
    @abstractmethod
    def __init__(self,refresh_interval,local_miner_API_ip,local_miner_API_port):
        pass

    @property
    @abstractmethod
    def threads(self) -> int:
        pass

    @property
    @abstractmethod
    def hash_rate(self) -> int:
        pass

    @property
    @abstractmethod
    def hash_rate_units(self) -> HashRateUnits:
        pass

    @property
    @abstractmethod
    def blocks_found(self) -> int:
        pass

    @property
    @abstractmethod
    def cpu_freq(self) -> dict:
        pass

    @property
    @abstractmethod
    def uptime(self) -> int:
        pass

    @property
    @abstractmethod
    def miner_name(self) -> str:
        pass

    @property
    @abstractmethod
    def miner_connected(self) -> bool:
        pass

    @property
    @abstractmethod
    def miner_has_been_connected(self) -> bool:
        pass

    @miner_has_been_connected.setter
    @abstractmethod
    def miner_has_been_connected(self, state):
        pass

    @property
    @abstractmethod
    def refresh_interval_seconds(self) -> int:
        pass
