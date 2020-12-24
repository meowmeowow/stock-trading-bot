import alpaca_trade_api as tradeapi
import logging
import time
from bs4 import BeautifulSoup
import requests
import re

buyer = Owner()
key = 'PKBWMGEH1NCBWH953XVQ'
secert_key = 'N1SpfwrKlaRJdkUNkAKal5EdDkT5d2x5kR7x4K7G'

ws_url = 'wss://data.alpaca.markets'
conn = tradeapi.stream2.StreamConn(key, secert_key, base_url='https://paper-api.alpaca.markets',data_url=ws_url, data_stream='alpacadatav1')
api = tradeapi.REST(key, secert_key, base_url='https://paper-api.alpaca.markets') 


class Stock:
  def __init__(self, code,currentPrice):
    self.code = code
    self.currentPrice = currentPrice
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
    def __init__(self,code,currentPrice,boughtPrice):
        super().__init__(code,currentPrice)
        self.boughtPrice = boughtPrice
    ##########
    def get_BoughtPrice(self):
    	return(boughtPrice)
    def set_BoughtPrice(self,input):
    	self.boughtPrice = input
    ##########

class IntrestedStock(Stock):
    def __init__(self,code,currentPrice):
        super().__init__(code,currentPrice)
 

class Owner():
	def __init__(self):
		self.money;
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
		# alot of stuff make this uhh a



@conn.on(r'^account_updates$')
async def on_account_updates(conn, channel, account):
	account = api.get_account()
    #buyer.set_money(account.cash)
    #print(buyer.get_money())

def sort_stocks(stocks):
	pass

def add_stocks(allStocks,buyer):
	for i in range(len(allStocks)):
		x = True
		for x in range(len(buyer.i_stocks)):
			if allStocks[i][0] == buyer.i_stocks[x]:
				x = False
		if x == False:
			continue



def find_stocks(buyer):
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

			allStocks.append([id,diff])
	add_stocks(allStocks,buyer)


def open_Market():
	find_stocks(buyer);
def closed_Market():
