import argparse
from pprint import pprint

import ccxt
import yaml


def read_arguments():
    arg_parser = argparse.ArgumentParser(description='Distribute coins')
    arg_parser.add_argument('--config', type=str, default='config.yaml', help='config file; see example.yaml')
    arg_parser.add_argument('--debug', action='store_true', help='debug mode')
    arg_parser.add_argument('--dry-run', action='store_true', help='dry run mode')
    return arg_parser.parse_args()


def create_exchange(config):
    return ccxt.okx({
        'apiKey': config['api_key'],
        'secret': config['secret'],
        "password": config['password'],
        "options": {'defaultType': 'spot'},
    })


def read_config(path):
    with open(path) as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def main():
    args = read_arguments()

    config = read_config(args.config)

    okx = create_exchange(config['exchange']['okx'])
    b = okx.fetch_balance()
    pprint(b)


if __name__ == '__main__':
    main()
