# coding=UTF-8
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

def get_daily_summary(symbol, today, rows):
    data = []
    
    td = rows[0].find_all('td')
    close_price_string_check = td[0].text.strip()
    if close_price_string_check == '--':
        return data

    item = Profile_daily_summary()
    item.date = today
    item.symbol = symbol
    try:
        td = rows[0].find_all('td')
        item.close_price = float(td[0].text.strip())

        td = rows[1].find_all('td')
        item.offset_price = float(td[0].text.strip())

        td = rows[2].find_all('td')
        item.offset_percent = float(td[0].text.strip('%'))
        item.open_price = float(td[1].text.strip())

        td = rows[3].find_all('td')
        item.high_price = float(td[0].text.strip())

        td = rows[4].find_all('td')
        item.qty = int(td[0].text.strip())
        item.low_price = float(td[1].text.strip())

        data.append(item)
    except:
        raise
    
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

def get_qty_price_profile(symbol, today, rows):
    data = []
    try:
        for row in rows[1:]:
            cols = row.find_all('td')
            item = Profile_qty_price()
            item.date = today
            item.symbol = symbol
            item.price = float(cols[0].text.strip())
            item.qty = int(cols[1].text.strip())
            #item.price = float(pattern.match(cols[0].text.strip()).group())
            #item.qty = float(pattern.match(cols[1].text.strip()).group())
            #print(item.date, item.symbol, item.price, item.qty)
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

    run_log_file="./outputs/run.log"
    error_log_file="./outputs/error.log"

    conn = sqlite3.connect('stock.sqlite3')
    cursor = conn.cursor()

    now = datetime.utcnow() + timedelta(hours=8) - timedelta(days=1)
    today = str(int(now.strftime('%Y%m%d')))
    
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
    for item in symbol_list:
        # this line of code is used for develop
        #if run_flag == 1:
        #    break

        delay_time = randint(5,9)
        time.sleep(delay_time)
        the_symbol = str(item[0])
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
            #raise ValueError('A very specific bad thing happened')

            #http://traderoom.cnyes.com/tse/quote2FB_HTML5.aspx?code=1101
            #url = "http://traderoom.cnyes.com/tse/quote2FB_HTML5.aspx?code=2102"
            url = "http://traderoom.cnyes.com/tse/quote2FB_HTML5.aspx?code="+ str(item[0])
            res = requests.get(url, timeout=30)
            soup = BeautifulSoup(res.text.encode("utf-8"),'lxml')

            # parse Profile_daily_summary
            table_real0 = soup.find('div', id='real_0').find('table')
            rows = table_real0.find_all('tr')
            insert_data = get_daily_summary(the_symbol, today, rows)
            #for a in insert_data:
                #print(a.date, a.symbol, a.open_price, a.close_price)
            for item in insert_data:
                cursor.execute('INSERT INTO Profile_daily_summary VALUES (?,?,?,?,?,?,?,?,?)', (item.date, item.symbol, item.open_price, item.close_price, item.high_price, item.low_price, item.offset_price, item.offset_percent, item.qty))
            conn.commit()

            save_file = save_symbol_data_path + '/' + 'profile_daily_summary.csv'
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

            # parse Profile_open_close_qty_price
            table_real1 = soup.find('div', id='real_1').find('table')
            rows = table_real1.find_all('tr')
            insert_data = get_open_close_qty_price_profile(the_symbol, today, rows)
            #for a in insert_data:
                #print(a.date, a.symbol, a.price, a.qty, a.sort)
            for item in insert_data:
                cursor.execute('INSERT INTO Profile_open_close_qty_price VALUES (?,?,?,?,?)', (item.date, item.symbol, item.qty, item.price, item.sort))
            conn.commit()

            save_file = save_symbol_data_path + '/' + 'profile_openclose.csv'
            with open(save_file, 'a') as f:
                for item in insert_data:
                    item_string = item.date + ',' + \
                                  item.symbol + ','+ \
                                  str(item.qty) + ',' + \
                                  str(item.price) + ',' + \
                                  str(item.sort)
                    f.write(item_string + '\n') 
            

            # Profile_qty_price
            table_real2 = soup.find('div', id='real_2').find('table')
            rows = table_real2.find_all('tr')
            insert_data = get_qty_price_profile(the_symbol, today, rows)
            #for a in insert_data:
                #print(a.date, a.symbol, a.price, a.qty)
            for item in insert_data:
                cursor.execute('INSERT INTO Profile_qty_price VALUES (?,?,?,?)', (item.date, item.symbol, item.qty, item.price))
            conn.commit()

            save_file = save_symbol_data_path + '/' + today + '_detail.csv'
            with open(save_file, 'w') as f:
                for item in insert_data:
                    item_string = item.date + ',' + \
                                  item.symbol + ','+ \
                                  str(item.qty) + ',' + \
                                  str(item.price)
                    f.write(item_string + '\n') 


        except:
            print('error on ', the_symbol)
            print(sys.exc_info()[0])
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
    ##schedule.every(1).minutes.do(run_all)
    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)
        
