import definitions
import exchange

import dataset
import ccxt

import pandas as pd

from abc import ABC, abstractmethod
from datetime import datetime


class World(ABC):

    """
    World: Connection with external services which provides exchange information and also receive trading orders.
    """

    def __init__(self):

        """
        + Description: constructor
        + Input:
        -
        + Output:
        -
        """

        pass

    @abstractmethod
    def is_connected(self):
        pass
        
    @abstractmethod
    def request_orderbook(self, ticker, exchange):
        pass

    @abstractmethod
    def request_candles(self, ticker, exchange, timeframe, since, limit):
        pass

    @abstractmethod
    def request_tickers(self, exchange):
        pass
    
    @abstractmethod
    def request_balance(self, exchange):
        pass

    @abstractmethod
    def request_tweets_count(self, filter):
        pass


class EmulatedWorld(World):

    """
    EmulatedWorld: Connection with databases and ficticious accounts.
    Inherit from World.
    """

    def __init__(self, data_elements):

        """
        + Description: constructor. Initializes corresponding data.
        + Input:
        - data_elements: data modules description built by user in config.
        + Output:
        -
        """

        super().__init__()
        self._initialize_data(data_elements)
        self.test_count = 0


    def _initialize_data(self, data_elements):

        """
        + Description: Initializes backtest data.
        + Input:
        - data_elements: data modules description built by user in config.
        + Output:
        -
        """

        data = {}
        for data_element in data_elements:
            data[definitions.data_id] = data_element[definitions.data_id]
            data[definitions.ticker] = data_element[definitions.description]
            data[definitions.exchange] = data_element[definitions.source]
            data[definitions.values] = self._load_data(data_element)

    def _load_data(self, data_element):

        """
        + Description: Load particular data.
        + Input:
        - data_element: data module description built by user in config.
        + Output:
        -
        """

        print("\nInitializing data module:")
        print("Description:", data_element[definitions.description])
        print("Source:", data_element[definitions.source])
        print("Data type:", data_element[definitions.data_type])
        if data_element[definitions.data_format] == definitions.csv:
            return self._load_data_from_csv(data_element)

        elif data_element[definitions.data_format] == definitions.sql:
            return  self._load_data_from_sql(data_element)

        elif data_element[definitions.data_format] == definitions.nosql:
            return  self._load_data_from_nosql(data_element)

        else:
            raise ValueError("Bad data_format.")

    def _load_data_from_csv(self, data_element):

        """
        Description: load data from csv into a dict of pandas elements.
        + Input:
        - data_element: data module description built by user in config.
        + Output:
        - data values: a pandas object or a None object.
        """

        filename = data_element[definitions.file_name]
        data = None
        try:
            data = pd.read_csv(filename, parse_dates=True)
        except:
            raise ValueError("ERROR trying to find csv file: "+filename+".")
        else:
            pd.to_datetime(data["datetime"])
            data.set_index("datetime", inplace=True)
        return data

    def _load_data_from_sql(self, data_element):

        """
        Description: load data from sql into a dict of pandas elements.
        + Input:
        - data_element: data module description built by user in config.
        + Output:
        - data values: a pandas object or a None object.
        """

        db = dataset.connect(data_element[definitions.db_path])
        table_name = data_element[definitions.table_name]
        header_format = data_element[definitions.header_format]   
        table = None     
        if header_format == definitions.cdm:
            table = pd.read_sql(sql=table_name,
                                con=db,
                                parse_dates="datetime",
                                index_col="datetime")
        else:
            raise ValueError("ERROR trying to read sql tables with header_format: '"
                            +header_format+"'.")
        return table
    
    def _load_data_from_nosql(self, data_element):

        """
        Description: load data from nosql into a dict of pandas elements.
        + Input:
        - data_element: data module description built by user in config.
        + Output:
        - data values: a pandas object or a None object.
        """
        
        data = None
        return data

    def is_connected(self):
        self.test_count += 1
        if self.test_count>10:
            return False
        return True

    def request_orderbook(self, ticker, exchange):

        """
        + Description: query to request orderboooks for a given ticker.
        + Input:
        - ticker: string
        - exchange: exchange name string
        + Output:
        - orderbook: array of dicts
        """
        
        return {"bids":[0,1,2], "asks":[0,1,2]}

    def request_candles(self, ticker, exchange, timeframe, since=None, limit=1000):

        """
        + Description: query to request candles for a given ticker.
        + Input:
        - ticker: string
        - exchange: exchange name string
        - timeframe: string        
        - since: seconds passed since the first required candle
        - limit: maximum amount of candles
        + Output:
        - candles: array of dicts
        """

        return {
            "datetime":[10100101,10120020202],
            "o":[1.1,2.2],
            "h":[1.1,2.2],
            "l":[1.1,2.2],
            "c":[1.1,2.2],
            "v":[1.1,2.2]
            }

    def request_tickers(self, exchange):
        
        """
        + Description: query to request tickers data.
        + Input:
        - ticker: string
        - exchange: exchange name string
        + Output:
        - tickers: array of dicts
        """

        return {
            "btcusd":{
                "last":1232
            },
            "ethusd":{
                "last":123
            }
        }

    def request_balance(self, exchange):

        """
        + Description: query to request exchange balances.
        + Input:
        - exchange: exchange name string
        + Output:
        - balance: dict with accounts balances.
        """

        return self._get_test_balance()

    def _get_test_balance(self):
        
        """
        + Description: test balance.
        + Input:
        -
        + Output:
        - balance: dict with accounts balances.
        """        
        
        balance = {
            definitions.trading:{
                definitions.usd:100,
                definitions.btc:100,
                definitions.eth:100
            },
            definitions.funding:{
                definitions.usd:0
            },
            definitions.margin_trading:{
                definitions.usd:100,
                definitions.btc:100,
                definitions.eth:100,
                definitions.margin:100
            }
        }

        return balance

    def request_tweets_count(self, filter):

        """
        + Description: query to request actual tweets filtered count.
        + Input:
        - filter: array of keyword strings to filter twitter stream.
        + Output:
        - tweets_count: Dictionary with datetime and integer twitter count.
        """

        tweets_count = {datetime.now(), 1000}
        return tweets_count

class RealWorld(World):

    """
    RealWorld: Connection with exchanges.
    Inherit from World.
    """

    def __init__(self, mode, exchanges_names, api_keys_files = None):

        """
        + Description: constructor
        + Input:
        -
        + Output:
        -
        """

        super().__init__()
        self.mode = mode
        if self.mode == definitions.real:
            self.exchanges = self._create_clients_with_private_connections(exchanges_names, api_keys_files)

    def _create_clients_with_private_connections(self, exchanges_names, api_keys_files):
        
        """
        + Description: create clients which connects whith exchanges using API.
        Clients are connected via private keys to enable using private methods.
        + Input:
        - exchanges_names: list of strings with exchanges names.
        - keys: dict of api keys.
        + Output:
        - list of exchanges clients.
        """

        exchanges = []
        for exchange in exchanges_names:

            keys = self._load_api_keys(api_keys_files[exchange])

            if exchange == definitions.bittrex:
                exchange.append(exchange.Bittrex(keys))
            
            elif exchange == definitions.binance:
                exchange.append(exchange.Binance(keys))
            
            elif exchange == definitions.bitfinex:
                exchange.append(exchange.Bitfinex(keys))
            
            else:
                raise ValueError("Exchange: "+exchange+" has not private connection implemented")
        
        return exchanges

    def _load_api_keys(self, api_key_file):

        """
        + Description: load exchange api keys.
        + Input:
        - api_key_file: string file name where keys are located.
        + Output:
        - dict of api keys, using ccxt format.
        """

        keys = {
            'apiKey':None,
            'secret':None
        }

        try:
            api_key_file = open(api_key_file, "r")
            keys['apiKey'] = api_key_file.readline()
            if(keys['apiKey'][-1]=="\n"):
                keys['apiKey'] = keys['apiKey'][:-1]
            keys['secret'] = api_key_file.readline()
            if(keys['secret'][-1]=="\n"):
                keys['secret'] = keys['secret'][:-1]
            api_key_file.close()
        
        except:
            raise ValueError("ERROR: Trying to read key file: "+api_key_file)

        return keys

    def is_connected(self):
        return True

    def request_orderbook(self, ticker, exchange):

        """
        + Description: query to request orderboooks for a given ticker.
        + Input:
        - ticker: string
        - exchange: exchange name string
        + Output:
        - orderbook: array of dicts
        """
        
        pass

    def request_candles(self, ticker, exchange, timeframe, since=None, limit=1000):

        """
        + Description: query to request candles for a given ticker.
        + Input:
        - ticker: string
        - exchange: exchange name string
        - timeframe: string        
        - since: seconds passed since the first required candle
        - limit: maximum amount of candles
        + Output:
        - candles: array of dicts
        """

        client = getattr(ccxt, exchange)()
        tickers = client.fetch_ohlcv(ticker, timeframe, since, limit)
        return tickers

    def request_tickers(self, exchange):
        
        """
        + Description: query to request tickers data.
        + Input:
        - ticker: string
        - exchange: exchange name string
        + Output:
        - tickers: array of dicts
        """

        pass

    def request_balance(self, exchange):

        """
        + Description: query to request exchange balances.
        + Input:
        - exchange: exchange name string
        + Output:
        - balance: dict with accounts balances.
        """

        pass

    def request_tweets_count(self, filter):

        """
        + Description: query to request actual tweets filtered count.
        + Input:
        - filter: array of keyword strings to filter twitter stream.
        + Output:
        - tweets_count: Dictionary with datetime and integer twitter count.
        """

        tweets_count = {datetime.now(), 1000}
        return tweets_count


class Oracle(object):

    """
    Oracle: Fast information from databases or real world.
    """

    def __init__(self, world):

        """
        + Description: constructor
        + Input:
        - current world
        + Output:
        -
        """

        super().__init__()
        self.world = world