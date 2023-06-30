import random
from datetime import datetime

from checkpointdb import CheckPointDatabase
from utils import get_asset_and_network


class Dispatcher:
    def __init__(self, actions, addresses, db: CheckPointDatabase):
        self.actions = actions
        self.addresses = addresses
        self.db = db

    @staticmethod
    def key(address, action):
        act_type = action['type']
        asset, network = get_asset_and_network(action)
        return f'{address}/{act_type}/{network}.{asset}'

    def mark_as_done(self, address, action, amount, result='good'):
        key = self.key(address, action)
        self.db.set_checkpoint(key, {
            'result': result,
            'action': action['type'],
            'date': datetime.now().isoformat(),
            'timestamp': datetime.now().timestamp(),
            'amount': amount,
        })

    def is_done(self, address, action):
        key = self.key(address, action)
        return bool(self.db.get_checkpoint(key))

    @property
    def all_combinations(self):
        for address in self.addresses:
            for action in self.actions:
                yield address, action

    def get_amount(self, action):
        amount = action['amount']
        if amount == 'random':
            min_amount = float(action['min'])
            max_amount = float(action['max'])

            r = random.uniform(min_amount, max_amount)

            round_decimals = action.get('round', 3)
            return round(r, round_decimals)
        else:
            return float(amount)

    def next_action(self):
        combos = list(self.all_combinations)
        random.shuffle(combos)
        for address, action in combos:
            if not self.is_done(address, action):
                return address, action
