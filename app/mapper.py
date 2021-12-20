import json
from typing import List

from requests import ReadTimeout

from .contract import ContractConnector
from .event_analyzer import TransferEventAnalyzer
from .models.token import Token
from .models.transfer import Transfer
from .utils import generate_block_ranges


class Mapper:
    def __init__(self, ethereum_node_uri, contract_address, partition_size, max_number_of_retries, logger, abi_endpoint):
        self.logger = logger
        self.max_number_of_retries = max_number_of_retries
        self.partition_size = partition_size
        self.watch_contract = False
        self.event_analyzer = TransferEventAnalyzer()
        self.contract = ContractConnector(ethereum_node_uri, contract_address, logger, abi_endpoint)
        name, symbol, supply, decimals = self.contract.get_basic_information()
        self.token = Token(name, symbol, supply, decimals)

    def start_mapping(self, starting_block, ending_block, minimum_block_height=0):
        if starting_block == 'contract_creation':
            starting_block = '0x0'

        if ending_block == 'latest':
            ending_block = self.contract.get_latest_block_number()
            self.watch_contract = True

        self.logger.info(
            'Started gathering state of token %s from block %s to %s' % (self.token.name, starting_block, ending_block))
        self._partition_blocks_and_gather_state(self.token, starting_block, ending_block, self.partition_size)
        self.logger.info(
            'Ended gathering state of token %s from block %s to %s' % (self.token.name, starting_block, ending_block))


    def _partition_blocks_and_gather_state(self, token, starting_block, ending_block, partition_size, retry_count=1):
        events = []
        for start, end in generate_block_ranges(starting_block, ending_block, partition_size):
            try:
                if start > end:
                    continue
                self.logger.info('Gather data of token %s from block %s to %s' % (token.name, start, end))
                events.extend(self.contract.get_state(start, end))
            except ReadTimeout as exception:
                self._try_to_retry_mapping(token, start, ending_block, partition_size, retry_count, exception)

        transfers = self.event_analyzer.get_events(events) # type: List[Transfer]

        with open('data.json', 'w') as fp:            
            print(json.dumps([ob.__dict__ for ob in transfers]), file=fp)

    def _try_to_retry_mapping(self, token, new_starting_block, ending_block, partition_size, retry_count, exception):
        if retry_count > self.max_number_of_retries:
            raise exception

        self.logger.warning('Encounter requests.exceptions.ReadTimeout. Retry for %i time' % retry_count)
        self._partition_blocks_and_gather_state(token, new_starting_block, ending_block, partition_size, retry_count + 1)
