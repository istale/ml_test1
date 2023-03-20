# coding=utf-8
import os
import sys
import sqlite3
from datetime import date
from datetime import datetime
from datetime import timedelta
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
import schedule
import traceback
import json
import shutil

def get_daily_summary(symbol, today, soup):
    data = []

    table_real0 = soup.find('th', text='漲跌').parent.parent
    rows = table_real0.find_all('tr')
    
    # https://tw.stock.yahoo.com/q/q?s=1101
    # rows[0] is table hearder
    # rows[1] is value
    td = rows[1].find_all('td')

    item = Profile_daily_summary()
    item.date = today
    item.symbol = symbol
    try:

        # check if this stock has data for today
        today_trade_qty = td[6].text.strip()
        if '－' in today_trade_qty:
            print('no trade today, so no profile_daily_summary')
            item.qty = 0
            #item.open_price = yesterday_price
            #item.close_price = yesterday_price 
            #item.high_price = yesterday_price
            #item.low_price = yesterday_price
            #item.offset_price = float( 0.00 )
            #item.offset_percent = float(0.0000)
        else:
            yesterday_price = float(td[7].text.strip())
            item.qty = int(td[6].text.strip().replace(',',''))
            item.open_price = float(td[8].text.strip())
            item.close_price = float(td[2].text.strip())
            item.high_price = float(td[9].text.strip())
            item.low_price = float(td[10].text.strip())
            item.offset_price = float( round(item.close_price - yesterday_price, 2 ) )
            item.offset_percent = float(round(item.offset_price/yesterday_price, 4))

        data.append(item)
    except:
        print('error when get profile_daily_summary on this stock: ' + str(symbol))
        item.qty = 0
        data.append(item)

    return data

def get_open_close_qty_price_profile(symbol, today, rows):
    data = []

    if len(rows) == 1:
        return data

    try:
        cols_first_row = rows[1].find_all('td')
        close_item = Profile_open_close_qty_price()
        close_item.date = today
        close_item.symbol = symbol
        close_item.price = float(cols_first_row[3].text.strip())
        close_item.qty = int(cols_first_row[5].text.strip())
        close_item.sort = 0
        data.append(close_item)

        row_number = len(rows)
        cols_last_row = rows[row_number-1].find_all('td')
        open_item = Profile_open_close_qty_price()
        open_item.date = today
        open_item.symbol = str(symbol)
        open_item.price = float(cols_last_row[3].text.strip())
        open_item.qty = int(cols_last_row[5].text.strip())
        open_item.sort = 1
        data.append(open_item)
    except:
        raise

    return data

def get_qty_price_profile(symbol, today, soup):
    data = []

    # data can be find in script tags
    if soup.find(text='本日尚無量價變化圖') != None:
        print('no trade today, so no profile_qty_price data')
        return data

    table_real2 = soup.find('td', text='本 日 量 價 變 化 圖').parent.parent
    target_string = table_real2.find('script').string
    pattern = re.compile(' var data=\[(.*?)\];')
    match = pattern.search(target_string)

    # group(0) --> var data =...   ,   group(1) -->  [[...]]
    data_string = match.group(1).strip()
    data_string = re.sub("\s+", "", data_string)
    data_string = data_string \
                .replace('],[', 'zzz').replace('[', '').replace(']', '').replace("'", "")
    list_datas = data_string.split('zzz')
    #for x in list_datas:
    #    print(x)

    try:
        for this_data in list_datas:
            list_temp = this_data.split(',')
            item = Profile_qty_price()
            item.date = today
            item.symbol = symbol
            item.price = float(list_temp[0])
            item.qty = int(list_temp[1])

            data.append(item)
    except:
        raise

    return data

def check_if_market_closed(check_date):
    with open('market_close_date', 'r') as f:
        for line in f:
            line=line.strip('\n')   # strip newline
            if line == check_date:
                return 1
        return 0

def run_all():
    #now = datetime.utcnow() + timedelta(hours=8) - timedelta(days=0)
    #today = str(int(now.strftime('%Y%m%d')))
    #print(today)
    #return

    run_log_file="./outputs/run.log"
    error_log_file="./outputs/error.log"

    conn = sqlite3.connect('stock.sqlite3')
    cursor = conn.cursor()

    outputs_path = './outputs'
    outputs_bak_path = './outputs_bak'
    if os.path.isdir(outputs_bak_path):
        shutil.rmtree(outputs_bak_path)
    shutil.copytree(outputs_path, outputs_bak_path)

    # auto run
    now = datetime.utcnow() + timedelta(hours=8) - timedelta(days=0)
    today = str(int(now.strftime('%Y%m%d')))

    # custom run
    #today = '20180620'

    save_file_path_base = './outputs/tw'
    
    #cursor.execute('select * from Market_close_date where close_date=?', (today,))
    #market_close_flag = cursor.fetchone()
    market_close_flag = check_if_market_closed(today)
    if market_close_flag == 1:
        print('***************************************')
        print('*                                     *')
        print('*        market close at {}     *'.format(today))
        print('*                                     *')
        print('***************************************')
        return
    else:
        print('')
        print('***************************************')
        print('*                                     *')
        print('*      Porcess start for {}     *'.format(today))
        print('*                                     *')
        print('***************************************')
        print('')

    run_log_channel = open(run_log_file, 'a')
    run_log_channel.write('\n' + today + ' start..')
    run_log_channel.close()

    cursor.execute('select symbol from Stocks')
    symbol_list = cursor.fetchall()
    total_stocks = len(symbol_list)

    pattern = re.compile(r"[+-]?\d+(?:\.\d+)?")

    loop_start_time = datetime.now()
    run_flag = 0
    for this_symbol in symbol_list:
        # this line of code is used for develop
        #if run_flag == 1:
        #    break

        delay_time = randint(3,6)
        time.sleep(delay_time)
        the_symbol = str(this_symbol[0])

        # debug use
        # the_symbol = '1470'
        
        run_flag = run_flag + 1
        run_percentage = round(run_flag / total_stocks * 100)
        loop_current_time = datetime.now()
        current_duration = loop_current_time - loop_start_time
        current_minutes, current_seconds = divmod(current_duration.seconds, 60)
        print('{} -- {} ({}, {}%) -- {} min {} sec'.format(the_symbol, run_flag, total_stocks, run_percentage, current_minutes, current_seconds))

        # check if folder created
        save_symbol_data_path = save_file_path_base + '/' + the_symbol
        os.makedirs(save_symbol_data_path, exist_ok=True)

        try:
            # below line is used to raise an exception to develop try catch
            # raise ValueError('A very specific bad thing happened')
            
            # from Taiwn Trade center
            #url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20180621&stockNo=2330'
            #url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY? \
            #       response=json& \
            #       date={}& \
            #       stockNo={}'.format(today, the_symbol)

            # from yahoo but sometime no data
            url = "https://tw.stock.yahoo.com/q/q?s="+ str(the_symbol)
            res = requests.get(url, timeout=30)
            
            # check if this stock is still exist, 200 means success
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text.encode("utf-8"),'lxml')

            # parse Profile_daily_summary --------------------------------------------------------
            insert_data = get_daily_summary(the_symbol, today, soup)
            #for a in insert_data:
            #    print(a.date, a.symbol, a.open_price, a.close_price)
            
            # if this day does not trade any 
            if len(insert_data) > 0:
                if insert_data[0].qty == 0:
                    continue
            
#            for item in insert_data:
#                cursor.execute('INSERT INTO Profile_daily_summary VALUES (?,?,?,?,?,?,?,?,?)', (item.date, item.symbol, item.open_price, item.close_price, item.high_price, item.low_price, item.offset_price, item.offset_percent, item.qty))
#            conn.commit()
#
            save_file = save_symbol_data_path + '/' + 'profile_daily_summary.csv'
            if not os.path.isfile(save_file):
                with open(save_file, 'a') as f:
                    f.write('date,symbol,open_price,close_price,high_price,low_price,offset_price,offset_percent,qty')
                    f.write('\n')

            with open(save_file, 'a') as f:
                for item in insert_data:    
                    item_string = item.date + ',' + \
                                  item.symbol + ','+ \
                                  str(item.open_price) + ',' + \
                                  str(item.close_price) + ',' + \
                                  str(item.high_price) + ',' + \
                                  str(item.low_price) + ',' + \
                                  str(item.offset_price) + ',' + \
                                  str(item.offset_percent) + ',' + \
                                  str(item.qty)
                    f.write(item_string + '\n')

            # parse Profile_open_close_qty_price ------------------------------------------------
            #table_real1 = soup.find('div', id='real_1').find('table')
            #rows = table_real1.find_all('tr')
            #insert_data = get_open_close_qty_price_profile(the_symbol, today, rows)
            ##for a in insert_data:
            #    #print(a.date, a.symbol, a.price, a.qty, a.sort)
            #for item in insert_data:
            #    cursor.execute('INSERT INTO Profile_open_close_qty_price VALUES (?,?,?,?,?)', (item.date, item.symbol, item.qty, item.price, item.sort))
            #conn.commit()

            #save_file = save_symbol_data_path + '/' + 'profile_openclose.csv'
            #with open(save_file, 'a') as f:
            #    for item in insert_data:
            #        item_string = item.date + ',' + \
            #                      item.symbol + ','+ \
            #                      str(item.qty) + ',' + \
            #                      str(item.price) + ',' + \
            #                      str(item.sort)
            #        f.write(item_string + '\n') 

            # Profile_qty_price ----------------------------------------------------------------
            url = "https://tw.stock.yahoo.com/q/ts?s=" + str(the_symbol)
            res = requests.get(url, timeout=30)
            soup = BeautifulSoup(res.text.encode("utf-8"),'lxml')

            insert_data = get_qty_price_profile(the_symbol, today, soup)
            #for a in insert_data:
                #print(a.date, a.symbol, a.price, a.qty)
            #for item in insert_data:
            #    cursor.execute('INSERT INTO Profile_qty_price VALUES (?,?,?,?)', (item.date, item.symbol, item.qty, item.price))
            #conn.commit()

            save_file = save_symbol_data_path + '/' + 'profile_qty_price.csv'
            if not os.path.isfile(save_file):
                with open(save_file, 'a') as f:
                    f.write('date,symbol,qty,price')
                    f.write('\n')

            with open(save_file, 'a') as f:
                for item in insert_data:
                    item_string = item.date + ',' + \
                                  item.symbol + ','+ \
                                  str(item.qty) + ',' + \
                                  str(item.price)
                    f.write(item_string + '\n') 


        except:
            print('error on ', the_symbol)
            print(sys.exc_info()[0])
            print(traceback.format_exc())
            with open(error_log_file, 'a') as f:
                f.write(today + ' error on ' + the_symbol + ' :\n\n')
                f.write(traceback.format_exc())
                f.write('------------------------------------------------------------\n')
            continue

    loop_end_time = datetime.now()

    total_duration = loop_end_time - loop_start_time
    total_minutes, total_seconds = divmod(total_duration.seconds, 60)
    print('\n\nTotal duration: {} min {} sec'.format(total_minutes, total_seconds))
    print('\n' + today + ' done.')

    run_log_channel = open(run_log_file, 'a')
    run_log_channel.write('..done, ' + 'Total duration: {} min {} sec'.format(total_minutes, total_seconds))
    run_log_channel.close()

if __name__ == '__main__':
    print('')
    print('***************************')
    print('*                         *')
    print('*      Porcess start      *')
    print('*                         *')
    print('***************************')
    print('')
    #below line is used for develop
    run_all()

    # 需要知道今天是否有開盤
    #schedule.every().day.at("17:00").do(run_all)
    #schedule.every().day.at("13:13").do(run_all)
    #schedule.every(1).minutes.do(run_all)
    #schedule.every().day.at("9:00").do(run_all)
    run_flag = 1
    while True:
        schedule.run_pending()
        time.sleep(1.5)
        run_flag = run_flag + 1
        if run_flag > 5:
            run_flag = 1
        output_string = 'i will have ' + ' 10 Billion! ' * run_flag
        print(' '*100, end='\r')
        print(output_string, end='\r')


