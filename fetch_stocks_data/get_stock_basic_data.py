# coding=UTF-8
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import lxml
import re
from entities import Stock

def get_stock_basic_data(url, grouping, remark):

    conn = sqlite3.connect('stock.sqlite3')
    cursor = conn.cursor()

    res = requests.get(url)
    soup = BeautifulSoup(res.text.encode("utf-8"),'lxml')


    table = soup.find('table', class_='h4')

    data = []
    rows = table.find_all('tr')
    for row in rows[2:]:   # 1-->2
        cols = row.find_all('td')
        if len(cols) < 7:
        	continue

        if cols[5].text.strip() == 'ESVUFR':
        	temp_stock_symbol_name = cols[0].text.strip().replace(' ', '')  #1101台泥
        	length_of_temp_stock_symbol_name = len(temp_stock_symbol_name)
        	symbol = temp_stock_symbol_name[0:4]
        	name = temp_stock_symbol_name[4:length_of_temp_stock_symbol_name]
        	stock = Stock()
        	stock.symbol = symbol
       		stock.name = name
        	stock.grouping = grouping
        	stock.remark = remark
        	print('{}\t{}\t{}\t{}'.format(stock.symbol.encode('utf-8'), stock.name.encode('utf-8'), stock.grouping.encode('utf-8'), stock.remark.encode('utf-8')))
        	data.append(stock)

    for item in data:
        cursor.execute('INSERT INTO Stocks VALUES (?,?,?,?)', (item.symbol, item.name, item.grouping, item.remark))

    conn.commit()

def get_current_stocks_in_table():
    list_return = []

    conn = sqlite3.connect('stock.sqlite3')
    cursor = conn.cursor()

    cursor.execute('select symbol from Stocks')
    symbol_list = cursor.fetchall()

    return symbol_list


if __name__ == '__main__':
    # 上市股票
    url = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    get_stock_basic_data(url, 'ex', '')  # ex for exchange

    # 上櫃股票
    url = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
    get_stock_basic_data(url, 'otc', '') # otc for OTC (Over-the-counter)
    
