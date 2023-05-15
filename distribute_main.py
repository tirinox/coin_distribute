import argparse
import time
from pprint import pprint

import ccxt
import colorama
import yaml
from ccxt import Exchange
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
    print(f'{Fore.GREEN}Reading config from {path!r}')
    with open(path) as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def delim():
    print(Fore.BLUE + '-' * 80)


def show_balance(exchange: Exchange):
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


def main():
    args = read_arguments()
    colorama.init()

    dry_run = args.dry_run

    config = read_config(args.config)

    db = CheckPointDatabase(config['name'])
    dispatcher = Dispatcher(config['actions'], config['addresses'], db)

    exchange = create_exchange(config['exchange'])
    show_balance(exchange)

    executor = Executor(exchange, dry_run)

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
