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
    def __init__(self,code,currentPrice,percentChange,boughtPrice,amount):
        super().__init__(code,currentPrice,percentChange)
        self.boughtPrice = boughtPrice
        self.amount = amount # check if this works
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
    self.account = api.get_account()
    self.limit = 0
  def set_money(self,input):
    self.money = input

  def find_buy(self,limit_cash,amount_of_stock):
    #starting_cash = api.account.cash  ????????????
    for i, stock in enumerate(self.i_stocks[:]):
      try:
        value = self.buy(stock, amount_of_stock)
        #print(value)
      except:
        continue
      if value == False:
        print()
        continue

      self.i_stocks.remove(stock)
      #print(value.code)
      self.o_stocks.append(value)
      #print("added" + value.code)


  def compare_money_made(self,stock):
      percentChangePerStock = ((stock.currentPrice-stock.boughtPrice)/stock.boughtPrice)*100
      return(percentChangePerStock)
  def stock_profit(self):
    #for i in range(len(self.o_stocks)):
    for i, stock in enumerate(self.o_stocks[:]):
      change = self.compare_money_made(stock)
      if change == 0:
        #continue
        self.sell(stock)
        self.o_stocks.remove(stock)
        print("sold")
      elif change > 0:
        if change > 0.1: # make this a class var
          self.sell(stock)
          self.o_stocks.remove(stock)
          print("sold")
      elif change < 0:
        if change < -0.1:
          self.sell(stock)
          self.o_stocks.remove(stock)
          print("sold")


  def buy(self,intrestedStock,num):
    #try:
    #print(intrestedStock.code,intrestedStock.currentPrice,intrestedStock.percentChange)
    if 1 == 1:
      try:
        info = self.get_info_stocks(intrestedStock.code)
        #newStock = OwnedStock(intrestedStock.code,intrestedStock.currentPrice,intrestedStock.percentChange,info[1],amount_of_stock)
        newStock = OwnedStock(intrestedStock.code,intrestedStock.currentPrice,intrestedStock.percentChange,info[1],num)
        #print(newStock.code)
      except:
        print("failed")
      try:
        api.submit_order( # check if order went through
        symbol=intrestedStock.code,
        side='buy',
        type='market',
        qty=num,
        time_in_force='day',
        #order_class='bracket',
        #take_profit=dict(
        #    limit_price='305.0',
        #),
        #stop_loss=dict(
        #    stop_price='295.5',
        #    limit_price='295.5',
        #)
        )
        return(newStock)
      except:
        return(False)


    #except:
    #  return(False)
		
  def sell(self,ownedStock):
    api.submit_order(
      symbol=ownedStock.code,
      side='sell',
      type='market',
      qty=ownedStock.amount,
      time_in_force='day',
      #order_class='bracket',
      #take_profit=dict(
      #    limit_price='305.0',
      #),
      #stop_loss=dict(
      #    stop_price='295.5',
      #    limit_price='295.5',
      #)
      )

  def add(self,code,currentPrice,percentChange):
    newStock_i = IntrestedStock(code,currentPrice,percentChange)
    self.i_stocks.append(newStock_i)

  def delate(self,intrestedStock):
    self.i_stocks.remove(intrestedStock)
  def update_i(self):
    for i in range(len(self.i_stocks)):
      info = self.get_info_stocks(self.i_stocks[i].code)
      self.i_stocks[i].currentPrice = info[1]
      self.i_stocks[i].percentChange = info[0]
  def update_self(self):
    #updates money + stocks owned
    pass
  def update_o(self):
    for i in range(len(self.o_stocks)):
      info = self.get_info_stocks(self.o_stocks[i].code)
      self.o_stocks[i].currentPrice = info[1]
      self.o_stocks[i].percentChange = info[0]


    
  def sort_stocks_i(self):
    for i in range(1,len(self.i_stocks)):
        item_to_insert = self.i_stocks[i].percentChange
        # And keep a reference of the index of the previous element
        j = i - 1
        # Move all items of the sorted segment forward if they are larger than
        # the item to insert
        while j >= 0 and self.i_stocks[j].percentChange > item_to_insert:
            self.i_stocks[j + 1].percentChange = self.i_stocks[j].percentChange
            j -= 1
        # Insert the item
        self.i_stocks[j + 1].percentChange = item_to_insert
    #self.print_stock()

  def get_info_stocks(self,stock):
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

  def add_stocks(self,allStocks):
    #stocks = []
    for i in range(len(allStocks)):
      #print(allStocks[i])

      x = True
      if len(self.i_stocks) != 0:
        for j in range(len(self.i_stocks)):        
          if allStocks[i] == self.i_stocks[j].code:
            x = False

      if x == False:
        continue
      info_about_stock = self.get_info_stocks(allStocks[i])
      if info_about_stock == False:
        continue
      else:
        #stocks.append(allStocks[i])
        #print(allStocks[i])
        newStock = self.add(allStocks[i],info_about_stock[1],info_about_stock[0])



  def print_stock_i(self):
    for i in range(len(self.i_stocks)):
      print(self.i_stocks[i].code,self.i_stocks[i].currentPrice,self.i_stocks[i].percentChange )
  def print_stock_o(self):
    if len(self.o_stocks) == 0:
      print("empty")
    for i in range(len(self.o_stocks)):
      print(self.o_stocks[i].code,self.o_stocks[i].currentPrice,self.o_stocks[i].percentChange )



  def find_stocks(self):
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
    

  def find_stocks(self):
    allStocks = ['F?p=ES=F', 'F?p=YM=F', 'F?p=NQ=F', 'FCEL', 'SRNE', 'MGNI', 'WHGRF', 'AEBZY', 'FBASF', 'LGF-A', 'LGF-B', 'LMND', 'GWLLF', 'SBGI', 'PMVP', 'CPYYF', 'NVAX', 'ALFFF', 'RIDE', 'M', 'NDBKY', 'LLDTF', 'VEDL', 'LYG', 'MGA', 'GCPEF', 'LESL', 'SWN']
    return (allStocks)


def time_to_market_close():
  clock = api.get_clock()
  return (clock.next_close - clock.timestamp).total_seconds()


def wait_for_market_open():
  clock = api.get_clock()
  if not clock.is_open:
    time_to_open = (clock.next_open - clock.timestamp).total_seconds()
    print(time_to_open)
    time.sleep(round(time_to_open))




def start(buyer):
  while(True):
    # wait_for_market_open() check if this works 
    #add stocks to already in account to list
    #buyer.print_stock_o()

    allStocks = buyer.find_stocks()
    buyer.add_stocks(allStocks)
    buyer.update_i()


    buyer.sort_stocks_i()


    print("i stocks before being bought: ")
    buyer.print_stock_i()

    buyer.find_buy(100,10)

    print("i stocks after being bought: ")
    buyer.print_stock_i()

    print("o stocks after being bought: ")
    buyer.print_stock_o()

    
    #update owned stocks
    print("selling")
    time.sleep(1)

    buyer.update_o() # this doesnt work well
    buyer.print_stock_o()
    buyer.stock_profit()
    print("o stocks after being sold: ")

    buyer.print_stock_o()
    break


    # make a function that checks if a stock increases in the past 30 mins


    #check if stocks owned decrease in price UPDATE EVERYTHING TO MINUETE
    #if some decrease by a certian amount than sell them
    # then buy more 
    # also add time stuff
    #restart everything at the end of the day



    #account = api.get_account()
    

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