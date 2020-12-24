import os, sys, argparse
import alpaca_trade_api as tradeapi
import logging
import time
from bs4 import BeautifulSoup
import requests
import re
import threading
key = 'PKBWMGEH1NCBWH953XVQ'
secert_key = 'N1SpfwrKlaRJdkUNkAKal5EdDkT5d2x5kR7x4K7G'

ws_url = 'wss://data.alpaca.markets'
conn = tradeapi.stream2.StreamConn(key, secert_key, base_url='https://paper-api.alpaca.markets',data_url=ws_url, data_stream='alpacadatav1')
api = tradeapi.REST(key, secert_key, base_url='https://paper-api.alpaca.markets') 

class Stock:
  def __init__(self, code,currentPrice,percentChange):
    self.code = code
    self.currentPrice = currentPrice
    self.percentChange = percentChange
  ##########
  def get_Code(self):
  	return(code)
  def get_CurrentPrice(self):
  	return(currentPrice)
  def set_Code(self,input):
  	self.code = input
  def set_CurrentPrice(self,input):
  	self.currentPrice = input
  ##########
class OwnedStock(Stock):
    def __init__(self,code,currentPrice,percentChange,boughtPrice):
        super().__init__(code,currentPrice,percentChange)
        self.boughtPrice = boughtPrice
    ##########
    def get_BoughtPrice(self):
      return(boughtPrice)
    def set_BoughtPrice(self,input):
      self.boughtPrice = input
    ##########

class IntrestedStock(Stock):
    def __init__(self,code,currentPrice,percentChange):
        super().__init__(code,currentPrice,percentChange)


class Owner():
	def __init__(self):
		self.money = 0
		self.o_stocks = []
		self.i_stocks = []
	def set_money(self,input):
		self.money = input

	def buy(self,intrestedStock):
		self.i_stocks.remove(intrestedStock)
		# add to the other list lol
	def sell(self,ownedStock):
		self.o_stocks.remove(ownedStock)
	def add(self,code,currentPrice):
		newStock_i = IntrestedStock(code,currentPrice)
		self.i_stocks.append(newStock_i)

	def delate(self,intrestedStock):
		self.i_stocks.remove(intrestedStock)
	def update(self):
		pass


def time_to_market_close():
	clock = api.get_clock()
	return (clock.next_close - clock.timestamp).total_seconds()


def wait_for_market_open():
	clock = api.get_clock()
	if not clock.is_open:
		time_to_open = (clock.next_open - clock.timestamp).total_seconds()
		sleep(round(time_to_open))


def sort_stocks(stocks):
  pass

def get_info_stocks(stock):
  try:
    barset = api.get_barset(stock, 'day', limit=1)
    aapl_bars = barset[stock]

    week_open = aapl_bars[0].o
    week_close = aapl_bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    currentValue = week_close
    #print(stock,week_open,week_close)
    return([percent_change,currentValue])
  except:
    return(False)

def add_stocks(allStocks,buyer):
  #stocks = []
  for i in range(len(allStocks)):
    #print(allStocks[i])

    x = True
    if len(buyer.i_stocks) != 0:
      for j in range(len(buyer.i_stocks)):        
        if allStocks[i] == buyer.i_stocks[j].code:
          x = False

    if x == False:
      continue
    info_about_stock = get_info_stocks(allStocks[i])
    if info_about_stock == False:
      continue
    else:
      #stocks.append(allStocks[i])
      #print(allStocks[i])
      newStock = IntrestedStock(allStocks[i],info_about_stock[1],info_about_stock[0])
      buyer.i_stocks.append(newStock)



def print_stock(stock):
  for i in range(len(stock)):
    print(stock[i].code,stock[i].currentPrice,stock[i].percentChange )


def find_stocks():
  r = requests.get("https://finance.yahoo.com/gainers").text
  soup = BeautifulSoup(r,"html.parser")
  #alldata = soup.find_all("body")
  links = []
  for link in soup.find_all("a", href=lambda href: href and "quote" in href):
    links.append(link.get('href'))

  allStocks = []
  for i in range(len(links)):
    #text = ("https://finance.yahoo.com" + (str((links[i]))))
    #print(text)
    r = requests.get("https://finance.yahoo.com" + (str((links[i])))).text
    soup = BeautifulSoup(r,"html.parser")

    thing = soup.find_all("span", {"class" : "Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)"})

    id = links[i][(re.search("=", links[i]).start())+1:]

    diff = None
    if len(thing) == 1:
      parts = thing[0].text.split()
      diff = parts[0]

      allStocks.append(id)
  return (allStocks)
  

def find_stocks():
  allStocks = ['F?p=ES=F', 'F?p=YM=F', 'F?p=NQ=F', 'FCEL', 'SRNE', 'MGNI', 'WHGRF', 'AEBZY', 'FBASF', 'LGF-A', 'LGF-B', 'LMND', 'GWLLF', 'SBGI', 'PMVP', 'CPYYF', 'NVAX', 'ALFFF', 'RIDE', 'M', 'NDBKY', 'LLDTF', 'VEDL', 'LYG', 'MGA', 'GCPEF', 'LESL', 'SWN']
  return (allStocks)

def start(buyer):
  allStocks = find_stocks()
  add_stocks(allStocks,buyer)
  print_stock(buyer.i_stocks)

  while(True):
    #wait_for_market_open()
    # do other stuff
    account = api.get_account()
    print(account)
    break

  #ws_start()

  #@conn.on(r'^account_updates$') 
  ##start WebSocket in a thread
  #ws_thread = threading.Thread(target=ws_start, daemon=True)
  #ws_thread.start()
  #time.sleep(30)

def parse_args(argv):
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=__doc__)

  parser.add_argument("-t", "--test", dest="test_flag", 
                    default=False,
                    action="store_true",
                    help="Run test function")
  parser.add_argument("--log-level", type=str,
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Desired console log level")
  parser.add_argument("-d", "--debug", dest="log_level", action="store_const",
                      const="DEBUG",
                      help="Activate debugging")
  parser.add_argument("-q", "--quiet", dest="log_level", action="store_const",
                      const="CRITICAL",
                      help="Quite mode")
  #parser.add_argument("files", type=str, nargs='+')

  args = parser.parse_args(argv[1:])

  return parser, args

def main(argv, stdout, environ):
  buyer = Owner()

  if sys.version_info < (3, 0): reload(sys); sys.setdefaultencoding('utf8')

  parser, args = parse_args(argv)

  logging.basicConfig(format="[%(asctime)s] %(levelname)-8s %(message)s", 
                    datefmt="%m/%d %H:%M:%S", level=args.log_level)

  if args.test_flag:  test();   return

  start(buyer)

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)