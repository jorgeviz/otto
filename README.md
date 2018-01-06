# OTTO Crypto Trader

Application to retrieve cryptocurrencies' prices and execute trades along predefined rules over different exchanges.

Available Exchanges:

- Bitso

Available Currencies

- Bitcoin (BTC)
- Bitcoin Cash (BCH)
- Ethereum (ETH)
- Litecoin (LTC)
- Ripple (XRP)
- Mexican Peso (MXN)


## Status

Currently in Beta Version, able to perform automated trades taking in count rules in `config.json` file.

### Trading Process

- OttoCT initializes and fetches needed data (fees, balances, and limits) from each Currency-Pair in Bitso to set its initial Baseline.
- Depending on the configuration file it will monitor all indicated currency-pairs and whenever Otto finds a trade price exceeding fixed percentual boundaries, it performs the trade of the fixed amount of Major defined in the file as well.
- Before executing the transaction, Otto verifies whether is or not enough balance in the account and if the transaction is within Bitso's transaction limits.

## How to run it?

### Linux or MacOS

- Install `virtualenv`:

```bash
sudo pip install virtualenv
```

- Create virtualenv `virtualenv --python="$(which python2)" env` and source into it with `source env/bin/activate`
- Verify other `python` default version is set to `2.7.*`, it has not be tested in other versions.
- Install dependencies `pip install -r requirements.txt`
- Verify in [Bitso](https://bitso.com/developers) to get your API keys them set then as the following environmental variables: `BITSO_API_KEY` and `BITSO_API_SECRET`.
- Tune the `config.json` file with the amount in Major (Currency-pairs are expressed `Major_minor`) of trades you want to perform and the percentual selling and buying bounds.
- Now run `python main.py` to start OttoCT, if want to set it to the background run `nohup python main.py > otto.log 2>&1 &`
- Also, to visualize cryptos' variation you can run `python -m otto.plot $Major_minor` and substitute `$Major_minor` for the currency-pair you want to monitor so the Live Graph should start displaying.


### TODO

- Save Baselines
- Plot (Baseline, Boundaries, Last Price and Weighted Average Price) in the same figure per Currency-Pair
- Tune parameters to improve algorithm performance
- Add plots, metrics and UI to change rules
- Implement executables for deploy in Multiple platforms
- Add ML indices to better estimate and maximize profit

## LICENSE

The MIT License (MIT)

Copyright (c) 2018 Jorge Vizcayno
