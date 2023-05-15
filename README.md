# coin_distribute

Distributes coins from the exchange according specified rules

Exchanges supported:

- OKX

You can get the asset and network names from the text file in the "exchanges" folder.
For example, for AVAX on OKX, open exchanges/okx.txt and use Ctrl+F to find the following line:
```Symbol: AVAX | Network: Avalanche C-Chain | Withdrawal fee: 0.0064```
So `asset` is `AVAX` and `network` is `Avalanche C-Chain`.

## Installation

1. Install Python 3.9+
2. Install dependencies: `pip install -r requirements.txt`
3. Use `example.yaml` to create your own config file for example `1.yaml`
   1) Fill your credentials in the `exchange` block
   2) Compile the list of addresses in the `addresses` block. Note! Each address must be surrounded by quotes ""
   3) Fill the `actions`.
4. Run `python distribute_main.py --config 1.yaml`
5. If you want to start over, delete the checkpoint YAML file under `db` folder. Otherwise, the script won't execute the same action twice.