import random
import time

from ccxt import Exchange
from colorama import Fore


class Executor:
    def __init__(self, exchange: Exchange, dry_run: bool = False, sleep_time: int = 1):
        self.exchange = exchange
        self.sleep_time = sleep_time
        self.dry_run = dry_run

    @staticmethod
    def _dry_action(address, action, amount):
        print(f'{Fore.CYAN}Dry action. Sleeping...')
        time.sleep(random.uniform(1, 5))

    def execute(self, address: str, action: dict, amount: float):
        print(f'Executing {action} => {amount} => {address}')
        if self.dry_run:
            self._dry_action(address, action, amount)
        else:
            act_type = action['type']
            if act_type == 'withdraw':
                self._withdraw(address, action, amount)
            else:
                raise Exception(f'Unsupported action type: {act_type}')
        time.sleep(self.sleep_time)

    def _withdraw(self, address: str, action: dict, amount: float):

        symbol = action['asset'].upper()
        network = action['network']

        fee, chain_name = self.get_withdrawal_fee(symbol, network)

        print(f'Withdraw {amount} {symbol}.{network} with fee {fee}')

        self.exchange.withdraw(
            symbol, amount, address,
            params={
                "toAddress": address,
                "chain": chain_name,
                "dest": 4,
                "fee": fee,
                "pwd": '-',
                "amt": amount,
                "network": network
            }
        )

    def get_withdrawal_fee(self, symbol_withdraw, chain_name):
        exchange = self.exchange
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
