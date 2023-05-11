import argparse


def read_config_from_agrs():
    arg_parser = argparse.ArgumentParser(description='Distribute coins')
    arg_parser.add_argument('--config', type=str, default='config.yaml', help='config file; see example.yaml')
    arg_parser.add_argument('--debug', action='store_true', help='debug mode')
    arg_parser.add_argument('--dry-run', action='store_true', help='dry run mode')
    return arg_parser.parse_args()


def main():
    args = read_config_from_agrs()
    print(args)


if __name__ == '__main__':
    main()
