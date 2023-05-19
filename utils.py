import os
import sys

import colorama
from colorama import Fore


def delim():
    print(Fore.BLUE + '-' * 80)


def get_filename_without_extension(path):
    filename = os.path.basename(path)  # Get the base name from the path
    filename_without_extension = os.path.splitext(filename)[0]  # Split the filename and remove the extension
    return filename_without_extension


def get_asset_and_network(obj: dict):
    asset = obj.get('asset') or obj['symbol']
    network = obj.get('network') or obj['chain']
    return asset, network


# Define a custom exception handler
def exception_handler(type, value, traceback):
    # Print the exception type in red
    print(Fore.RED + f"Exception Type: {type.__name__}")

    # Print the exception value in red
    print(Fore.RED + f"Exception Value: {value}")

    # Print the traceback
    print("Traceback:")
    traceback.print_tb(traceback)


def setup_color_scheme():
    colorama.init()
    # Set the custom exception handler
    sys.excepthook = exception_handler
