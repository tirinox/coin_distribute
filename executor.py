import time

from ccxt import Exchange


class Executor:
    def __init__(self, exchange: Exchange, sleep_time: int = 1):
        self.exchange = exchange
        self.sleep_time = sleep_time

    def execute(self, address, action, amount):
        print(f'Executing {action} => {amount} => {address}')
        time.sleep(self.sleep_time)
