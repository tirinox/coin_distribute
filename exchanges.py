import ccxt
from colorama import Fore

from utils import delim


class ExchangeManager:
    def __init__(self, list_of_configs: list):
        self.exchanges = {}
        for config in list_of_configs:
            name, ex_type, exchange = self.create_exchange(config)
            name = str(name)
            if name in self.exchanges:
                raise Exception(f'Duplicated exchange name: {name}')
            self.exchanges[name] = exchange
            print(f'{Fore.CYAN}Loaded exchange: {name} ({ex_type})')
        print(f'{Fore.CYAN}Loaded {len(self.exchanges)} exchanges.')

    def show_balances(self):
        for name, exchange in self.exchanges.items():
            print(f'{Fore.CYAN}Loading exchange "{name}" balance...')
            self.show_balance(exchange)

    def get_exchange(self, name: str):
        if not name:
            if len(self.exchanges) == 1:
                return next(iter(self.exchanges.values()))
            else:
                raise Exception(f'Exchange name not specified and there are {len(self.exchanges)} exchanges.')
        return self.exchanges[str(name)]

    def withdraw(self, exchange_name: str, symbol: str, network: str, amount: float, address: str):
        exchange = self.get_exchange(exchange_name)
        if isinstance(exchange, ccxt.okx):
            self._okx_withdraw(exchange, symbol, network, amount, address)
        elif isinstance(exchange, ccxt.bybit):
            self._bybit_withdraw(exchange, symbol, network, amount, address)
        elif isinstance(exchange, (ccxt.mexc, ccxt.binance, ccxt.kucoin)):
            self._regular_withdraw(exchange, symbol, network, amount, address)
        else:
            raise Exception(f'Unsupported exchange: {exchange}')

    @staticmethod
    def create_exchange(config: dict):
        ex_type = config.get('type')
        if not ex_type:
            raise Exception(f'Exchange type not specified: {config}')
        ex_type = ex_type.lower()

        name = config.get('name') or config.get('tag') or config.get('label') or ex_type

        api_key = config.get('api_key') or config.get('key')
        api_secret = config.get('secret') or config.get('secret_key') or config.get('api_secret')
        password = config.get('password') or config.get('passphrase')

        if ex_type == 'okx':
            exchange = ccxt.okx({
                'apiKey': api_key,
                'secret': api_secret,
                "password": password,
                "options": {'defaultType': 'spot'},
            })
        elif ex_type == 'binance':
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        elif ex_type == 'mexc':
            exchange = ccxt.mexc({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })
        elif ex_type == 'kucoin':
            exchange = ccxt.kucoin({
                'apiKey': api_key,
                'secret': api_secret,
                'password': password,
                'enableRateLimit': True,
            })
        elif ex_type == 'bybit':
            exchange = ccxt.bybit({
                'apiKey': api_key,
                'secret': api_secret,
            })
        else:
            raise Exception(f'Unsupported exchange: {ex_type}!')

        return name, ex_type, exchange

    def show_balance(self, exchange):
        delim()
        print(f'{Fore.GREEN}Balance:')
        balances = exchange.fetch_balance()

        b_used = balances['used']
        b_total = balances['total']

        for asset, balance in b_total.items():
            if balance == 0:
                continue
            used = b_used[asset]
            print(f'{Fore.GREEN}    {asset}: {balance} (used: {used})')
        delim()

    def _okx_get_withdrawal_fee(self, exchange, symbol_withdraw, chain_name):
        currencies = exchange.fetch_currencies()
        for currency in currencies:
            if currency == symbol_withdraw:
                currency_info = currencies[currency]
                network_info = currency_info.get('networks', None)
                if network_info:
                    for network in network_info:
                        network_data = network_info[network]
                        network_id = network_data['network']
                        if network_id == chain_name:
                            withdrawal_fee = currency_info['networks'][network]['fee']
                            chain_full_name = network_data["info"]["chain"]
                            if withdrawal_fee == 0:
                                return 0
                            else:
                                return withdrawal_fee, chain_full_name
        raise ValueError(f"Cannot find withdrawal fee for {symbol_withdraw} {chain_name}")

    def _okx_withdraw(self, okx, symbol, network, amount, address):
        fee, chain_name = self._okx_get_withdrawal_fee(okx, symbol, network)
        okx.withdraw(
            symbol, amount, address,
            params={
                "toAddress": address,
                "chain": network,
                "dest": 4,
                "fee": fee,
                "pwd": '-',
                "amt": amount,
                "network": network
            }
        )

    @staticmethod
    def _regular_withdraw(ex, symbol, network, amount, address):
        ex.withdraw(
            code=symbol,
            amount=amount,
            address=address,
            params={
                "network": network
            }
        )

    @staticmethod
    def _bybit_withdraw(ex, symbol, network, amount, address):
        ex.withdraw(
            code=symbol,
            amount=amount,
            address=address,
            tag=None,
            params={
                "forceChain": 1,
                "network": network
            }
        )
