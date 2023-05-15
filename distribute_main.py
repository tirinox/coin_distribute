import argparse
import time

import ccxt
import colorama
import yaml
from colorama import Fore

from checkpointdb import CheckPointDatabase
from dispatcher import Dispatcher
from executor import Executor

SLEEP_AFTER_ERROR = 10


def read_arguments():
    arg_parser = argparse.ArgumentParser(description='Distribute coins')
    arg_parser.add_argument('--config', type=str, default='config.yaml', help='config file; see example.yaml')
    arg_parser.add_argument('--debug', action='store_true', help='debug mode')
    arg_parser.add_argument('--dry-run', action='store_true', help='dry run mode')
    return arg_parser.parse_args()


def create_exchange(config):
    for key in config.keys():
        if key == 'okx':
            sub_cfg = config[key]
            return ccxt.okx({
                'apiKey': sub_cfg['api_key'],
                'secret': sub_cfg['secret'],
                "password": sub_cfg['password'],
                "options": {'defaultType': 'spot'},
            })
        else:
            raise Exception(f'Unsupported exchange: {key}')


def read_config(path):
    with open(path) as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def delim():
    print(Fore.BLUE + '-' * 80)


def main():
    args = read_arguments()
    colorama.init()

    config = read_config(args.config)

    db = CheckPointDatabase(config['name'])
    dispatcher = Dispatcher(config['actions'], config['addresses'], db)

    exchange = create_exchange(config['exchange'])
    executor = Executor(exchange)
    # b = exchange.fetch_balance()
    # pprint(b)

    while do := dispatcher.next_action():
        address, action = do
        amount = dispatcher.get_amount(action)
        key = dispatcher.key(address, action)

        try:
            delim()
            print(f'{Fore.GREEN}Processing {key} => {amount} => {address}')
            executor.execute(address, action, amount)
        except Exception as e:
            print(f'{Fore.RED}Error: {e}! Sleeping...')
            time.sleep(SLEEP_AFTER_ERROR)
        else:
            dispatcher.mark_as_done(address, action, amount)
            print(f'{Fore.GREEN}Done!')

    print(f'{Fore.GREEN}All done!{Fore.RESET}')


if __name__ == '__main__':
    main()
