from binance.client import Client
from binanceAPI.position_utilities import enter_long, enter_short
from data.triple_list import TripleList
from config import api_key, secret_key
from indicators.price import fetch_price
from indicators.rsi import fetch_RSI
from indicators.fetch_all_indicators import fetch_all_indicators
from tensorflow_utilities.tensorflow_decision import predict
from data.io_utilities import print_with_color, calculateWR, get_current_date_string
from time import sleep
from data.data_functions import save_result, save_position
import copy

# Binance API initialization
client = Client(api_key, secret_key)

# Global Variable Declarations
price = 0
state = 2
on_long = False
on_short = False
tp_price = 0
sl_price = 0
tp_count = 0
sl_count = 0
csv_path_result = "./data/ragebot_result.csv"
csv_path_dataset = "./data/ragebot_dataset.csv"
date = ""
data_position = None
data_check = None
pseudo = None
triple_log = TripleList()

# Global Functions
def close_position(isTP):
    global on_long
    global on_short
    global tp_count
    global sl_count 
    global csv_path_result
    global csv_path_dataset
    global date
    global state
    global pseudo

    position = ""

    if (on_long and isTP) or (on_short and (not isTP)): 
        position = "LONG"
    elif (on_long and (not isTP)) or (on_short and isTP):
        position = "SHORT"

    save_position(csv_path_dataset, position, data_position)
    
    if on_long and isTP:
        state = state + 1 if (state != 3) else 3
    elif on_long and (not isTP):
        state = state - 1
    elif on_short and isTP:
        state = state - 1 if (state != 0) else 0
    elif on_short and (not isTP):
        state = state + 1

    on_long = False
    on_short = False

    if not pseudo:
        save_result(csv_path_result, data_position.date, position, "LONG" if on_long else "SHORT")
        if isTP:
            tp_count = tp_count + 1
            print_with_color("green", "Position closed with TP")
            print_with_color("yellow", "TP: " + str(tp_count) + " SL: " + 
                str(sl_count) + " Win-Rate: " + calculateWR(tp_count, sl_count))
        else:
            sl_count = sl_count + 1
            print_with_color("red", "Position closed with SL")
            print_with_color("yellow", "TP: " + str(tp_count) + " SL: " + 
                str(sl_count) + " Win-Rate: " + calculateWR(tp_count, sl_count))
    else:
        print_with_color("cyan", "dataset is updated")

print_with_color("cyan", "RageBot is running...\n")

while True:
    try:
        sleep(10)
        data_check = fetch_all_indicators(client)

        if not (on_long or on_short):
            data_position = copy.deepcopy(data_check)
            _, prediction = predict(csv_path_dataset, data_position)
            triple_log.add(prediction)
            pseudo = True

            if state == 3:
                if triple_log.confirm("LONG"):
                    pseudo = False
                tp_price, sl_price = enter_long(client, pseudo)
                on_long = True
                print()
                if not pseudo:
                    print_with_color("yellow", "Entered LONG Current: " + str(round(data_check.price, 2)) + 
                    " TP_PRICE: " + str(round(tp_price, 2)) + " SL_PRICE: " + str(round(sl_price, 2)))
            
            elif state == 2:
                tp_price, sl_price = enter_long(client, pseudo)
                on_long = True

            elif state == 1:
                tp_price, sl_price = enter_short(client, pseudo)
                on_short = True
                
            elif state == 0:
                if triple_log.confirm("SHORT"):
                    pseudo = False
                tp_price, sl_price = enter_short(client, pseudo)
                on_short = True
                print()
                if not pseudo:
                    print_with_color("yellow", "Entered SHORT Current: " + str(round(data_check.price, 2)) + 
                    " TP_PRICE: " + str(round(tp_price, 2)) + " SL_PRICE: " + str(round(sl_price, 2)))

        else:
            if (on_long and data_check.price > tp_price) or \
                (on_short and data_check.price < tp_price):
                close_position(True)
            elif (on_long and data_check.price < sl_price) or \
                (on_short and data_check.price > sl_price):
                close_position(False)

    except Exception as e:
        error_message = str(e)
        print_with_color("yellow", error_message)