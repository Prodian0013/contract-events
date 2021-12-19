from app.mapper import Mapper
from app.logger import init_logger
import logging

PARITY_NODE_URI = 'https://api.avax.network/ext/bc/C/rpc'
MAX_BLOCKS_TO_MAP_AT_ONCE = 15000
MAX_NUMBER_OF_RETRIES = 10
CONTRACT_ADDRESS = '0x6B8FB769d1957F2c29aBc9d1bEB95851cce775D8'
START_BLOCK = '7117331'
END_BLOCK = 'latest'
ABI_ENDPOINT = 'https://api.snowtrace.io/api?module=contract&action=getabi&address='

logger = logging.getLogger('main_logger')
init_logger(logger)

def map_token_state():
    mapper = Mapper(
        ethereum_node_uri=PARITY_NODE_URI,
        contract_address=CONTRACT_ADDRESS,
        partition_size=MAX_BLOCKS_TO_MAP_AT_ONCE,
        max_number_of_retries=MAX_NUMBER_OF_RETRIES,
        logger=logger,
        abi_endpoint=ABI_ENDPOINT)
    mapper.start_mapping(starting_block=START_BLOCK, ending_block=END_BLOCK)

if __name__ == '__main__':
    map_token_state()
