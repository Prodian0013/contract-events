# Contract Events
Pull web3 transfer events from contract on avalanche.

## Install dependencies and run 
```bash
pip3 install -r requirements.txt
```

## Usage
```
python3 run.py -h

usage: run.py [-h] [--get-events] [--address] [--start] [--end]
              [--process-data]

optional arguments:
  -h, --help      show this help message and exit
  --get-events    Pull contract event data from avax rpc
  --address       Contract Address
  --start         Start block (default: 0x0)
  --end           End block (default: latest)
  --process-data  Process event data from json (TODO)
```

Events will be stored in data.json by default.

Inspired by https://github.com/Exef/token-state-relational-mapper
