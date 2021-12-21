import asyncio
import json
from asyncio.locks import Semaphore
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from logging import Logger
from typing import List

from requests import ReadTimeout
from web3 import Web3

from .contract import ContractConnector
from .event_analyzer import TransferEventAnalyzer
from .models.token import Token
from .models.transfer import Transfer
from .utils import generate_block_ranges

_executor = ThreadPoolExecutor(3)


class Mapper:
    def __init__(self, ethereum_node_uri: str, contract_address: str, partition_size: str, max_number_of_retries: str, logger: Logger, abi_endpoint: str):
        self.logger = logger
        self.max_number_of_retries = max_number_of_retries
        self.partition_size = partition_size
        self.watch_contract = False
        self.event_analyzer = TransferEventAnalyzer()
        self.contract_connector = ContractConnector(ethereum_node_uri, contract_address, logger, abi_endpoint)
        name, symbol, supply, decimals = self.contract_connector.get_basic_information()
        self.token = Token(name, symbol, supply, decimals)
        self.events = []
        self.block_timestamps = {}

    def start_mapping(self, starting_block, ending_block, minimum_block_height=0):
        if starting_block == 'contract_creation':
            starting_block = '0x0'

        if ending_block == 'latest':
            ending_block = self.contract_connector.get_latest_block_number()
            self.watch_contract = True

        self.logger.info(
            'Started gathering state of token %s from block %s to %s' % (self.token.name, starting_block, ending_block))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._partition_blocks_and_gather_state(self.token, starting_block, ending_block, self.partition_size))

        self.logger.info(
            'Ended gathering state of token %s from block %s to %s' % (self.token.name, starting_block, ending_block))

    def get_timestamp(self, block_number) -> str:
        timestamp = self.contract_connector.web3.eth.get_block(block_number).timestamp
        dt_object = str(datetime.fromtimestamp(timestamp))
        self.block_timestamps[block_number] = dt_object
        return dt_object

    def get_events(self, start_from_block, end_at_block, retry_count=1):
        try:
            self.logger.debug(
            'Getting state of token from contract at address %s from block %s to %s' % (
                self.contract_connector.contract_address, start_from_block, end_at_block))
            transferEvents = self.contract_connector.contract.events.Transfer().createFilter(fromBlock=start_from_block, toBlock=end_at_block, argument_filters={})
            return  transferEvents.get_all_entries()
        except ReadTimeout as exception:
                self._try_to_retry_mapping(start_from_block, end_at_block, retry_count, exception)

    async def get_state(self, semaphore: Semaphore, start_from_block, end_at_block):
        await semaphore.acquire()
        loop = asyncio.get_event_loop()
        transfers = await loop.run_in_executor(ThreadPoolExecutor(5), self.get_events, start_from_block, end_at_block)

        if not transfers:
            transfers = []
        self.logger.debug(
            'Found %i transfers of token from contract at address %s from block %s to %s'
            % (len(transfers), self.contract_connector.contract_address, start_from_block, end_at_block))

        for t in transfers:
            event = json.loads(Web3.toJSON(t))
            block_number = event['blockNumber']
            timestamp = None
            if block_number in self.block_timestamps:
                timestamp = self.block_timestamps[block_number]
            else:
                timestamp = await loop.run_in_executor(ThreadPoolExecutor(5), self.get_timestamp, block_number)
            event['timestamp'] = timestamp
            self.events.append(event)

        self.logger.debug(
            '%i transfers added to event list from block %s to %s'
            % (len(transfers), start_from_block, end_at_block))

        semaphore.release()

    async def _partition_blocks_and_gather_state(self, token, starting_block, ending_block, partition_size):
        mySemaphore = asyncio.Semaphore(value=5)
        tasks = []
        for start, end in generate_block_ranges(starting_block, ending_block, partition_size):
            if start > end:
                continue
            self.logger.info('Gather data of token %s from block %s to %s' % (token.name, start, end))
            tasks.append(self.get_state(mySemaphore, start, end))

        await asyncio.wait(tasks)

        transfers_unsorted = self.event_analyzer.get_events(self.events) # type: List[Transfer]
        transfers = sorted(transfers_unsorted, key=lambda x: x.block_time)

        with open('data.json', 'w') as fp:
            print(json.dumps([ob.__dict__ for ob in transfers]), file=fp)

    def _try_to_retry_mapping(self, starting_block, ending_block, retry_count, exception):
        if retry_count > self.max_number_of_retries:
            raise exception

        self.logger.warning('Encounter requests.exceptions.ReadTimeout. Retry for %i time from block %s to %s' % (retry_count, starting_block, ending_block))
        self.get_events(starting_block, ending_block, retry_count + 1)
