import argparse
import logging
from logging import Logger

from app.logger import init_logger
from app.mapper import Mapper
from app.process import process_data

PARITY_NODE_URI = 'https://api.avax.network/ext/bc/C/rpc'
MAX_BLOCKS_TO_MAP_AT_ONCE = 15000
MAX_NUMBER_OF_RETRIES = 10
CONTRACT_ADDRESS = '0x6B8FB769d1957F2c29aBc9d1bEB95851cce775D8'
START_BLOCK = '7117331'
END_BLOCK = 'latest'
ABI_ENDPOINT = 'https://api.snowtrace.io/api?module=contract&action=getabi&address='


parser = argparse.ArgumentParser()
parser.add_argument("--get-events", help="Pull contract event data from avax rpc", dest='get_events', action='store_true')
parser.add_argument("--address", help="Contract Address", dest='contract_address', default=CONTRACT_ADDRESS)
parser.add_argument("--start", help="Start block (default: 7117331)", dest='start_block', default=START_BLOCK)
parser.add_argument("--end", help="End block (default: latest)", dest='end_block', default=END_BLOCK)
parser.add_argument("--process-data", help="Convert data json into spreadsheet", dest='process_data', action='store_true')
args, unknown = parser.parse_known_args()

logger = logging.getLogger('main_logger') # type: Logger


def map_token_state(contract_address, start_block, end_block):
    mapper = Mapper(
        ethereum_node_uri=PARITY_NODE_URI,
        contract_address=contract_address,
        partition_size=MAX_BLOCKS_TO_MAP_AT_ONCE,
        max_number_of_retries=MAX_NUMBER_OF_RETRIES,
        logger=logger,
        abi_endpoint=ABI_ENDPOINT,
        start_block=start_block,
        end_block=end_block)

    mapper.start_mapping()

if __name__ == '__main__':
    if not (args.get_events or args.process_data):
        parser.error('No action requested')
    init_logger(logger)
    if args.get_events:
        map_token_state(args.contract_address, args.start_block, args.end_block)
    elif args.process_data:
        process_data()
