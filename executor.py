import random
import time

from colorama import Fore

from exchanges import ExchangeManager
from utils import get_asset_and_network


class Executor:
    def __init__(self, exman: ExchangeManager, dry_run: bool = False, sleep_time: int = 1):
        self.exman = exman
        self.sleep_time = sleep_time
        self.dry_run = dry_run

    @staticmethod
    def _dry_action():
        print(f'{Fore.CYAN}Dry action. Sleeping...')
        time.sleep(random.uniform(1, 5))

    def execute(self, address: str, action: dict, amount: float):
        act_type = action['type']
        exchange_label = action.get('exchange')

        asset, network = get_asset_and_network(action)

        print(f'Executing {exchange_label} => {act_type} => {amount} {asset} / {network} => {address}')

        if act_type == 'withdraw':
            if self.dry_run:
                self._dry_action()
            else:
                self.exman.withdraw(exchange_label, asset, network, amount, address)
        else:
            raise Exception(f'Unsupported action type: {act_type}')

        time.sleep(self.sleep_time)
