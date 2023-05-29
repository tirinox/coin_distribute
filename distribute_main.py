import argparse
import time

import yaml
from colorama import Fore

from checkpointdb import CheckPointDatabase
from dispatcher import Dispatcher
from exchanges import ExchangeManager
from executor import Executor
from utils import delim, get_filename_without_extension, setup_color_scheme

SLEEP_AFTER_ERROR = 10


def read_arguments():
    arg_parser = argparse.ArgumentParser(description='Distribute coins')
    arg_parser.add_argument('-c', '--config', type=str, default='config.yaml', help='config file; see example.yaml')
    arg_parser.add_argument('--debug', action='store_true', help='debug mode')
    arg_parser.add_argument('-d', '--dry-run', action='store_true', help='dry run mode')
    return arg_parser.parse_args()


def read_config(path):
    print(f'{Fore.GREEN}Reading config from {path!r}')
    with open(path) as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def main():
    setup_color_scheme()
    args = read_arguments()

    dry_run = args.dry_run

    config = read_config(args.config)

    name = config.get('name')
    if not name:
        name = get_filename_without_extension(args.config)
    if not name:
        raise Exception('No name in config and no filename')

    db = CheckPointDatabase(name)
    dispatcher = Dispatcher(config['actions'], config['addresses'], db)

    exchange_manager = ExchangeManager(config['exchanges'])

    # todo: not yet implemented correctly
    # exchange_manager.show_balances()

    executor = Executor(exchange_manager, dry_run)

    while do := dispatcher.next_action():
        address, action = do
        amount = dispatcher.get_amount(action)
        key = dispatcher.key(address, action)

        try:
            delim()
            print(f'{Fore.GREEN}Processing {key} => {amount} => {address}')
            executor.execute(address, action, amount)
        except Exception as e:
            print(f'{Fore.RED}Error: {e!r}! Sleeping...')
            time.sleep(SLEEP_AFTER_ERROR)
        else:
            dispatcher.mark_as_done(address, action, amount)
            print(f'{Fore.GREEN}Done!')

    print(f'{Fore.GREEN}All done!{Fore.RESET}')


if __name__ == '__main__':
    main()
