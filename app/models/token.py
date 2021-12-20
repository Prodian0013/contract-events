class Token(object):
    def __init__(self, token_name, token_symbol, token_total_supply, token_decimals):
        self.name = token_name
        self.symbol = token_symbol
        self.total_tokens_supply = token_total_supply
        self.decimals = token_decimals