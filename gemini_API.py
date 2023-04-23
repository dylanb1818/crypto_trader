import json, requests
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime as dt
import hmac
import base64
import hashlib
import datetime
from PyQt5.QtWidgets import *
from google_sheets_API import GoogleSheetsService

class GeminiAPI(QMainWindow):
    def __init__(self):
        '''
        Initializes the API key and signature and URL
        Loads the GUI initializes the PyQt5 QMainWindow Class in Super__init__
        '''
        super().__init__()
        self.base_url = "https://api.gemini.com/v2"
        self.gemini_api_key = ""
        self.gemini_api_secret = "".encode()
        
        # Initialize GUI
        self.window = QWidget()
        self.GUI()

    def get_selected_option(self):
        '''
        Return correct crypto based on GUI option chosen. 
        Two options are btc and eth.
        '''
        if self.option_eth.isChecked():
            return 1
        elif self.option_btc.isChecked():
            return 2
        else:
            return None

    def get_limit_price(self):
        '''
        Sets the Limit Price from GUI textbox
        '''
        limit_price = self.limit_price.text()
        self.price = limit_price
        return limit_price
    
    def get_limit_amount(self):
        '''
        Sets the Limit Amount from GUI textbox
        '''
        limit_amount = self.limit_amount.text()
        self.amount = limit_amount
        return limit_amount

    def get_buy_or_sell(self):
        '''
        Sets the Order Type from GUI Checkbox
        '''
        if type(self.switch) != bool:
            self.switch = True
        elif self.switch:
            self.switch = False
        elif not self.switch:
            self.switch = True

    def GUI(self):
        '''
        Initializes the GUI with the options to: 
            - 15 minute candles data for 2 weeks from self.FifteenMinuteCandles()
            - Initialize buy or sell orders of btc/eth from self.limit_order()
        '''
        self.window.setWindowTitle('My Window')  # Set the window title
        self.window.setGeometry(100, 100, 400, 300)  # Set the window geometry

        # Buttons
        self.layout = QVBoxLayout()
        self.limit_price = QLineEdit()
        self.limit_amount = QLineEdit()
        button_fifteen_min_candles = QPushButton("15 min Candle Data")  
        self.option_btc = QRadioButton('btc')
        self.option_eth = QRadioButton('eth')
        price_label = QLabel('Set Limit Price')
        amount_label = QLabel('Set Limit Amount')
        self.switch = QCheckBox('Check for Buy Order, Leave for Sell Order', self)
        button_initiate_trade = QPushButton('Initiate Order')

        # google_sheets = QPushButton('sheets')

        # Layout
        self.layout.addWidget(button_fifteen_min_candles)
        self.layout.addWidget(price_label)
        self.layout.addWidget(self.limit_price)
        self.layout.addWidget(amount_label)
        self.layout.addWidget(self.limit_amount)
        self.layout.addWidget(self.option_btc)
        self.layout.addWidget(self.option_eth)
        self.layout.addWidget(self.switch)
        self.layout.addWidget(button_initiate_trade)
        # self.layout.addWidget(google_sheets)

        self.window.setLayout(self.layout)
    
        # Button Connections
        button_fifteen_min_candles.clicked.connect(lambda: self.FifteenMinuteCandles())
        button_initiate_trade.clicked.connect(lambda: self.limit_order(self.get_limit_price(), self.get_selected_option(), self.get_limit_amount()))  
        button_initiate_trade.clicked.connect(lambda: self.google_sheets())
        self.switch.stateChanged.connect(lambda: self.get_buy_or_sell())

        # google_sheets.clicked.connect(lambda: self.google_sheets())

        # Display Window
        self.window.show()
 
    def FifteenMinuteCandles(self):
        '''
        Gives 15 minute interval data points for Bitcoin and Ethereum over the last 2 weeks and plots it
        '''
        base_url = "https://api.gemini.com/v2"

        btc_response = requests.get(base_url + "/candles/btcusd/15m")
        btc_data = btc_response.json()
        btc_candle_data = pd.DataFrame(btc_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

        eth_response = requests.get(self.base_url + "/candles/ethusd/15m")
        eth_data = eth_response.json()
        eth_candle_data = pd.DataFrame(eth_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

        btc_time_data = [i[0] for i in btc_data]
        eth_time_data = [i[0] for i in eth_data]

        for i in range(len(btc_time_data)):
            btc_time_data[i] = str(dt.fromtimestamp(btc_time_data[i]/1000))
            # time_data[i] = time_data[i][11:19]

        for i in range(len(eth_time_data)):
            eth_time_data[i] = str(dt.fromtimestamp(eth_time_data[i]/1000))

        btc_time_data.reverse()
        eth_time_data.reverse()
        btc_close_data = [i[4] for i in btc_data]
        eth_close_data = [i[4] for i in eth_data]

        fig, (eth, btc) = plt.subplots(2, 1)
        eth.plot(eth_time_data, eth_close_data)
        eth.set_title('Ethereum')
        btc.plot(btc_time_data, btc_close_data)
        btc.set_title('Bitcoin')

        plt.show()

    def limit_order(self, input_price=None, crypto=None, input_amount=None):
        '''
        Set a limit buy order on the allowed cryptocurrencies
        '''
        self.crypto = crypto
        if input_price == None or crypto == None or input_amount == None:
            print('Invalid Input')
            return None
        
        if self.switch:
            side = 'buy'
        else:
            side = 'sell'

        crypto_dict = {2: ['btc', 'BTC', 'btcusd'], 1: ['eth', 'ETH', 'ethusd']}

        print(f'Placing a limit {side} order for {float(input_amount) * float(input_price)}$ of {crypto_dict[crypto][1]} at the limit price of {input_price}$')
        response = requests.get(f"https://api.gemini.com/v1/pubticker/{crypto_dict[crypto][1]}USD").json()
        price = float(response['ask'])
        print(f'Current Price of {crypto_dict[crypto][1]}: ', price)

        def Auth(payload):
            encoded_payload = json.dumps(payload).encode()
            b64 = base64.b64encode(encoded_payload)
            signature = hmac.new(self.gemini_api_secret, b64, hashlib.sha384).hexdigest()

            request_headers = { 'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': self.gemini_api_key,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache" }
            return(request_headers)
        
        base_url = "https://api.sandbox.gemini.com"
        endpoint = "/v1/order/new"
        url = base_url + endpoint
            
        t = datetime.datetime.now()
        payload_nonce =  str(int(time.mktime(t.timetuple())))  
        payload_nonce =  str(payload_nonce + '1')  

        payload = {
            "request": "/v1/order/new",
            "nonce": payload_nonce,
            "symbol": crypto_dict[crypto][2],
            "amount": input_amount,
            "price": input_price,
            "side": side,
            "type": "exchange limit",
            "account": "Primary"
             }
        
        new_order = requests.post(url,
                        data=None,
                        headers=Auth(payload)).json()

    def google_sheets(self):
        '''
        Conenct to Google Sheets and update row for given trade order
        '''

        SAMPLE_SPREADSHEET_ID = ''
        sheets = GoogleSheetsService(SAMPLE_SPREADSHEET_ID)
        col = int(sheets.read_value('readme', 'A', 1)['values'][0][0])
        
        if self.crypto == 1:
            symbol = 'ETH'
        elif self.crypto == 2:
            symbol = 'BTC'

        current_time = datetime.datetime.now()

        if self.switch:
            side = 'Buy'
        elif not self.switch:
            side = 'Sell'

        order_type = 'Limit'
        price = self.price
        quantity = self.amount
        total = int(self.price) * int(self.amount)

        sheets.update_value('Gemini_order_tab', 'A', col, symbol)
        sheets.update_value('Gemini_order_tab', 'B', col, current_time)
        sheets.update_value('Gemini_order_tab', 'C', col, side)
        sheets.update_value('Gemini_order_tab', 'D', col, order_type)
        sheets.update_value('Gemini_order_tab', 'E', col, price)
        sheets.update_value('Gemini_order_tab', 'F', col, quantity)
        sheets.update_value('Gemini_order_tab', 'G', col, total)

        sheets.update_value('readme', 'A', 1, col + 1)

