# coding=UTF-8
import sqlite3

class Stock:
	def __init__(self):
		self.symbol = ''
		self.name = ''
		self.grouping = ''
		self.remark = ''

class Profile_qty_price:
	def __init__(self):
		self.date = ''
		self.symbol = ''
		self.qty = 0
		self.price = 0

class Profile_open_close_qty_price:
	def __init__(self):
		self.date = ''
		self.symbol = ''
		self.qty = ''
		self.price = ''
		self.sort = ''				# 0 for open, 1 for close

class Profile_daily_summary:
	def __init__(self):
		self.date = ''
		self.symbol = ''
		self.open_price = 0
		self.close_price = 0
		self.high_price = 0
		self.low_price = 0
		self.offset_price = 0		#漲跌價格
		self.offset_percent = 0		#漲跌幅
		self.qty = 0				#成交量

def is_table_exist(pDatabase, pTable):
	"check if table exist"
	conn = sqlite3.connect(pDatabase)
	cursor = conn.execute("SELECT name FROM sqlite_master WHERE type=? AND name=?", ('table',pTable))
	is_table_exist = cursor.fetchone()
	return is_table_exist

def prepare_table():
	"create database tables"
	database_name = 'stock.sqlite3'
	conn = sqlite3.connect(database_name)
	cursor = conn.cursor()

	if is_table_exist(database_name, 'Stocks') == None:
	    cursor.execute('CREATE TABLE Stocks (symbol text, name text, grouping text, remark text)')
	    conn.commit()

	if is_table_exist(database_name, 'Profile_qty_price') == None:
	    cursor.execute('CREATE TABLE Profile_qty_price (date text, symbol text, qty real, price real)')
	    conn.commit()

	if is_table_exist(database_name, 'Profile_open_close_qty_price') == None:
	    cursor.execute('CREATE TABLE Profile_open_close_qty_price (date text, symbol text, qty real, price real, sort real)')
	    conn.commit()

	if is_table_exist(database_name, 'Profile_daily_summary') == None:
	    cursor.execute('CREATE TABLE Profile_daily_summary (date text, symbol text, open_price real, close_price real, high_price real, low_price real, offset_price real, offset_percent real, qty real)')
	    conn.commit()

	if is_table_exist(database_name, 'Market_close_date') == None:
		cursor.execute('CREATE TABLE Market_close_date (close_date text)')
		conn.commit()

if __name__ == '__main__':
	prepare_table()
