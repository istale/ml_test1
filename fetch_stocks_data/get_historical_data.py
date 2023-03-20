# coding=UTF-8
import sqlite3
from datetime import date
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import lxml
import re
from entities import Stock
from entities import Profile_qty_price
from entities import Profile_open_close_qty_price
from entities import Profile_daily_summary
import time
from random import randint
#import schedule
import csv
import os

# https://blog.ccjeng.com/2016/03/Yahoo-Finance-API.html
# https://greenido.wordpress.com/2009/12/22/work-like-a-pro-with-yahoo-finance-hidden-api/
# http://ichart.finance.yahoo.com/table.csv?g=d&f=2016&e=12&c=2007&b=10&a=7&d=7&s=2330.tw
# http://ichart.finance.yahoo.com/table.csv?a=01&b=01&c=2007&d=12&e=31&f=2015&g=d&ignore=.csv&s=2330.tw
# where the FROM date is: &a=01&b=10&c=2010
# and the TO date is: &d=01&e=19&f=2010

def get_yahoo_historical_csv_url(symbol, start, end, gap):
	# gap: d for day, m for month, y for year
	# http://ichart.finance.yahoo.com/table.csv?a=01&b=01&c=2007&d=12&e=31&f=2015&g=d&ignore=.csv&s=2330.tw

	start_date_list = start.split('-')
	start_year = start_date_list[0]
	start_month = "%02d" % (int(start_date_list[1]) - 1) # month start from 0
	start_day = start_date_list[2]

	end_date_list = end.split('-')
	end_year = end_date_list[0]
	end_month = "%02d" % (int(end_date_list[1]) - 1) # month start from 0
	end_day = end_date_list[2]

	url = "http://ichart.finance.yahoo.com/table.csv?" + \
			"a=" + start_month + "&" + \
			"b=" + start_day + "&" + \
			"c=" + start_year + "&" + \
			"d=" + end_month + "&" + \
			"e=" + end_day + "&" + \
			"f=" + end_year + "&" + \
			"g=" + gap +"&" + \
			"s=" + symbol + "&" + \
			"ignore=.csv"
	return url    


def run_all():

    conn = sqlite3.connect('stock.sqlite3')
    cursor = conn.cursor()

    cursor.execute('select symbol from Stocks where grouping="otc"')
    symbol_list = cursor.fetchall()
    total_stocks = len(symbol_list)

    now_time = datetime.now().strftime('%Y%m%d%H%M%S')
    run_flag = 0
    loop_start_time = datetime.now()
    for item in symbol_list:

    	#if run_flag == 3:
    		#break

    	delay_time = randint(5,9)
    	time.sleep(delay_time)
    	the_symbol = str(item[0])
    	run_flag = run_flag + 1
    	run_percentage = round(run_flag / total_stocks * 100)
    	loop_current_time = datetime.now()
    	current_duration = loop_current_time - loop_start_time
    	current_minutes, current_seconds = divmod(current_duration.seconds, 60)
    	print('{} -- {} ({}, {}%) -- {} min {} sec'.format(the_symbol, run_flag, total_stocks, run_percentage, current_minutes, current_seconds))

    	try:
    		symbol_str = the_symbol + ".TWO"
    		url = get_yahoo_historical_csv_url(symbol_str, '1900-01-01', '2016-12-31', 'd')
    		res = requests.get(url)
    		decoded_content = res.content.decode('utf-8')

    		file_folder = "./tw_otc/"
    		write_file_name = symbol_str.replace('.','_') + "_" + now_time + '.csv'
    		save_path = file_folder + write_file_name
    		os.makedirs(os.path.dirname(save_path), exist_ok=True)
    		with open(save_path, 'w') as f:
    			f.write(decoded_content)

    	except:
            print('error on: ', the_symbol)
            continue

    loop_end_time = datetime.now()

    total_duration = loop_end_time - loop_start_time
    total_minutes, total_seconds = divmod(total_duration.seconds, 60)
    print('\n\nTotal duration: {} min {} sec'.format(total_minutes, total_seconds))



if __name__ == '__main__':
    run_all()