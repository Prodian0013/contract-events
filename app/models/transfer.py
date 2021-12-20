class Transfer(object):
    def __init__(self, block_time, amount, to_address, from_address, timestamp):
        self.block_time = block_time
        self.amount = amount
        self.to_address = to_address
        self.from_address = from_address
        self.timestamp = timestamp
