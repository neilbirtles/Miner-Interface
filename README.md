# Miner-Interface
Miner Interface

These scripts provide a mechanism to standardise the publishing of information from crypto currency miners to allow centralised collation and display of the information by the SBC Miner (https://github.com/neilbirtles/SBC-crypto-miner-webapp). Interfaces to different miners must conform to the MinerInterfaceAbstract class

Setup the virtual environment to run this in 

`python3 -m venv venv` 

Activate the virtual environment

`source venv/bin/activate`

Then install the required packages

`pip install -r requirements.txt`

Then run the local publisher with 

`python MinerInfoLocalClient.py`

usage: commandlinetest.py [-h] [-L LOCALIP] [-l LOCALPORT] [-s SBCMINERIP] [-S SBCMINERPORT]

Standardised interface for crypto miners to the SBC Miner

optional arguments:
  -h, --help            show this help message and exit
  -L LOCALIP, --localip LOCALIP
                        IP address for the local miner, default: 127.0.0.1
  -l LOCALPORT, --localport LOCALPORT
                        API port number for the local miner, default: 4048
  -s SBCMINERIP, --sbcminerip SBCMINERIP
                        IP address for the SBC Miner, default: 10.0.0.250
  -S SBCMINERPORT, --sbcminerport SBCMINERPORT
                        Miner Info port number for the SBC Miner, default: 55440
