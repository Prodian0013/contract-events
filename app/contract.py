import json
from logging import Logger
from typing import Tuple

import requests
from web3 import HTTPProvider, Web3
from web3.eth import Contract
from web3.middleware import geth_poa_middleware


class ContractConnector:
    def __init__(self, ethereum_node_uri: str, contract_address: str, logger: Logger, abi_endpoint: str):

        self.logger = logger
        self.event_name = 'Transfer'
        self.contract_address = contract_address
        self.abi_endpoint = abi_endpoint

        self.web3 = Web3(HTTPProvider(ethereum_node_uri)) # type: Web3
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.address = self.web3.toChecksumAddress(contract_address)
        self.abi = self.fetch_abi()
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.address) # type: Contract
        self.block_timestamps = {}

    def fetch_abi(self) -> list:
        response = requests.get('%s%s'%(self.abi_endpoint, self.address))
        response_json = response.json()
        abi = json.loads(response_json['result']) # type: list
        return abi

    def get_basic_information(self) -> Tuple:
        self.logger.debug('Getting basic token information from contract at address %s' % self.contract_address)
        token_name = self.contract.functions.name().call()
        total_supply = self.contract.functions.totalSupply().call()
        token_symbol = self.contract.functions.symbol().call()
        token_decimal_places = self.contract.functions.decimals().call()

        return token_name, token_symbol, total_supply, token_decimal_places


    def get_latest_block_number(self):
        return self.web3.eth.blockNumber
