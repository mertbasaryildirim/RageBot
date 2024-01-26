from binance.client import Client
from binanceAPI.position_utilities import enter_long, enter_short
from config import api_key, secret_key
from indicators.price import fetch_price
from indicators.rsi import fetch_RSI
from data.io_utilities import print_with_color, calculateWR, get_current_date_string
from time import sleep
from data.data_functions import save_result
import copy

# Binance API initialization
client = Client(api_key, secret_key)