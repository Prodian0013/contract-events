import json
from datetime import datetime

import requests
from web3 import HTTPProvider, Web3
from web3.eth import Contract
from web3.middleware import geth_poa_middleware
from web3._utils.events import get_event_data


class ContractConnector:
    def __init__(self, ethereum_node_uri, contract_address, logger, abi_endpoint):
        self.logger = logger
        self.event_name = 'Transfer'
        self.contract_address = contract_address
        self.abi_endpoint = abi_endpoint

        self.web3 = Web3(HTTPProvider(ethereum_node_uri)) # type: Web3
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.address = self.web3.toChecksumAddress(contract_address)
        self.abi = self.fetch_abi()
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.address) # type: Contract

    def fetch_abi(self):
        response = requests.get('%s%s'%(self.abi_endpoint, self.address))
        response_json = response.json()
        abi = json.loads(response_json['result'])
        return abi

    def get_basic_information(self):
        self.logger.debug('Getting basic token information from contract at address %s' % self.contract_address)
        token_name = self.contract.functions.name().call()
        total_supply = self.contract.functions.totalSupply().call()
        token_symbol = self.contract.functions.symbol().call()
        token_decimal_places = self.contract.functions.decimals().call()

        return token_name, token_symbol, total_supply, token_decimal_places

    def get_state(self, start_from_block, end_at_block):
        self.logger.debug(
            'Getting state of token from contract at address %s from block %s to %s' % (
                self.contract_address, start_from_block, end_at_block))

        transferEvents = self.contract.events.Transfer().createFilter(fromBlock=start_from_block, toBlock=end_at_block, argument_filters={})
        transfers = transferEvents.get_all_entries()
        all_events = []
        for t in transfers:
            event = json.loads(Web3.toJSON(t))
            timestamp = self.web3.eth.get_block(t['blockNumber']).timestamp
            dt_object = datetime.fromtimestamp(timestamp)
            event['timestamp'] = str(dt_object)
            all_events.append(event)
        self.logger.debug(
            'Found %i transfers of token from contract at address %s from block %s to %s'
            % (len(all_events), self.contract_address, start_from_block, end_at_block))

        return all_events

    def get_latest_block_number(self):
        return self.web3.eth.blockNumber
