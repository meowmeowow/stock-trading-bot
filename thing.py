import alpaca_trade_api as tradeapi
import time
from bs4 import BeautifulSoup
import requests
import re

key = 'PKGXJNJ7OIUT7XVGV3UF'
secert_key = 'iQgMfza100GBEbhifcMbhBDzFjVxdyrNNU50I1h2'
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
        self.amount = amount 
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
  def __init__(self,ogMoney):
    self.money = 0
    self.ogMoney = ogMoney
    self.o_stocks = []
    self.i_stocks = []
    self.account = api.get_account()
    self.limit = 0
    self.money_limit = 20000
  def set_money(self,input):
    self.money = input

  def find_buy(self,limit_cash,amount_of_stock):
    if float(self.money) <= (float(self.ogMoney)-float(self.money_limit)):
      return("no money")

    for i, stock in enumerate(self.i_stocks[:]):
      if self.limit-len(self.o_stocks) <= 0: 
        return()
      try:
        value = self.buy(stock, amount_of_stock,limit_cash)
        
      except Exception as e:
        print(value.code)
        print(e)
        continue
      if value == False:
        continue


      self.i_stocks.remove(stock)
      self.o_stocks.append(value)



  def compare_money_made(self,stock):
      percentChangePerStock = ((float(stock.currentPrice)-float(stock.boughtPrice))/float(stock.boughtPrice))*100
      return(percentChangePerStock)
  def stock_profit(self):
    for i, stock in enumerate(self.o_stocks[:]):
      change = self.compare_money_made(stock)
      if change == 0:
        continue
      elif change > 0:
        if change > 0.5: # make this a class var
          self.sell(stock)
      elif change < 0:
        if change < -0.5:
          self.sell(stock)
  def sell_everything(self):
    for i, stock in enumerate(self.o_stocks[:]):
      self.sell(stock)
  def clear_everything():
    self.o_stocks = []
    self.i_stocks = []
  def get_amount_with_cash(self,limit_cash,price):
    return(limit_cash//price)


  def buy(self,intrestedStock,num,limit_cash):
    num = self.get_amount_with_cash(limit_cash,intrestedStock.currentPrice) -1
    if 1 == 1:
      try:
        info = self.get_info_stocks(intrestedStock.code)
        if info == False:
          return(False)
        newStock = OwnedStock(intrestedStock.code,intrestedStock.currentPrice,intrestedStock.percentChange,info[1],num)
      except:
        print("failed")
      try:
        api.submit_order( # check if order went through
        symbol=intrestedStock.code,
        side='buy',
        type='market',
        qty=num,
        time_in_force='day',
        )
        return(newStock)
      except:
        return(False)
		
  def sell(self,ownedStock):
    try:
      api.submit_order( # check if order went through
        symbol=ownedStock.code,
        side='sell',
        type='market',
        qty=ownedStock.amount,
        time_in_force='day',

        )
    except:
      return()
    self.o_stocks.remove(ownedStock)

  def add(self,code,currentPrice,percentChange):
    newStock_i = IntrestedStock(code,currentPrice,percentChange)
    self.i_stocks.append(newStock_i)

  def delate(self,intrestedStock):
    self.i_stocks.remove(intrestedStock)
  def update_i(self):
    for i in range(len(self.i_stocks)):
      info = self.get_info_stocks(self.i_stocks[i].code)
      if info == False:
        continue
      self.i_stocks[i].currentPrice = info[1]
      self.i_stocks[i].percentChange = info[0]
  def update_money(self):
    account = api.get_account()
    self.money = account.cash 
    
  def update_owned_stocks_start(self):
    stocks_things = api.list_positions()
    for i in range(len(stocks_things)):
      new_stock = OwnedStock(stocks_things[i].symbol,stocks_things[i].current_price,stocks_things[i].change_today,stocks_things[i].current_price, stocks_things[i].qty)
      self.o_stocks.append(new_stock)
  def update_o(self):
    for i in range(len(self.o_stocks)):
      info = self.get_info_stocks(self.o_stocks[i].code)
      if info == False:
        continue
      self.o_stocks[i].currentPrice = info[1]
      self.o_stocks[i].percentChange = info[0]


    
  def sort_stocks_i(self):
    for i in range(1,len(self.i_stocks)):
        item_to_insert = self.i_stocks[i].percentChange
        j = i - 1
        while j >= 0 and self.i_stocks[j].percentChange > item_to_insert:
            self.i_stocks[j + 1].percentChange = self.i_stocks[j].percentChange
            j -= 1
        self.i_stocks[j + 1].percentChange = item_to_insert

  def get_info_stocks(self,stock):
    try:
      #barset = api.get_barset(stock, 'day', limit=1)  
      barset = api.get_barset(stock, 'minute', limit=40)
      aapl_bars = barset[stock]

      week_open = aapl_bars[0].o
      week_close = aapl_bars[-1].c
      percent_change = (week_close - week_open) / week_open * 100
      currentValue = week_close
      return([percent_change,currentValue])
    except:
      return(False)

  def add_stocks(self,allStocks):
    for i in range(len(allStocks)):

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
    

def time_to_market_close():
  clock = api.get_clock()
  return (clock.next_close - clock.timestamp).total_seconds()


def wait_for_market_open():
  clock = api.get_clock()
  if not clock.is_open:
    time_to_open = (clock.next_open - clock.timestamp).total_seconds()
    print(time_to_open)
    time.sleep(round(time_to_open))

def check_if_market_open():
  clock = api.get_clock()
  return(clock.is_open)



def start():
  account = api.get_account()
  buyer = Owner(float(account.cash))

  time_min = 20
  buyer.limit = 100
  limit_cash = 250
  buyer.money_limit = 25000
  


  while(True):
    api.cancel_all_orders()
    wait_for_market_open() 

    buyer.update_money() 
    buyer.update_owned_stocks_start()

    while (True):
      if check_if_market_open() == False: 
        break
      if time_to_market_close() <= 60*60:
        buyer.sell_everything()
        buyer.clear_everything()
        break

      buyer.update_o() 
      buyer.update_i()



      if len(buyer.o_stocks) != 0:
        buyer.stock_profit() # change values here


      allStocks = buyer.find_stocks()
      buyer.add_stocks(allStocks)
      buyer.update_i()
      buyer.sort_stocks_i()

      buyer.update_money()
      buyer.find_buy(limit_cash,10) 


      print("o stocks: ")
      buyer.print_stock_o()
      print("i stocks: ")
      buyer.print_stock_i()
      print("   ")
      time.sleep(time_min*60) # change this
    
def test():
  stock = "AAPL"
  barset = api.get_barset(stock, 'day', limit=1)  #get current price
  aapl_bars = barset[stock]
  week_open = aapl_bars[0].o
  week_close = aapl_bars[-1].c

  account = api.get_account()
  buyer = Owner(float(account.cash))

  bars = api.get_barset("AAPL", 'minute', limit = 40)
  week_open = aapl_bars[0].o
  week_close = aapl_bars[-1].c
  percent_change = (week_close - week_open) / week_open * 100
  currentValue = week_close
  print([percent_change,currentValue])


  #print(bars)
  #allStocks[i][1] = (bars["APPL"][len(bars["APPL"]) - 1].c - bars["APPL"][0].o) / bars["APPL"][0].o


start()

#test()
