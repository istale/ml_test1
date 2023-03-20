import os
import sys
import glob
from scipy import stats

def get_list_file_path( path_representation ):
    #list = glob.glob('/home/raohongfu/*.php')
    list_return = glob.glob( path_representation  )
    #for this_path in list_return:
    #    print(this_path)
    return list_return

def get_list_symbol_from_outputs():
    file_path = './outputs/tw/*'
    list_symbol_path = get_list_file_path( file_path  )

    list_return = []
    for this_path in list_symbol_path:
        list_temp = this_path.split('/')
        list_return.append( list_temp[-1] )

    return sorted(list_return)


def read_csv_to_dict( input_table ):
    list_return = []

    list_header = []

    with open(input_table, 'r') as f:
        run_flag = 0

        for line in f:
            run_flag = run_flag + 1

            line = line.strip()

            if run_flag == 1:
                list_header = line.split(',')

            else:
                list_row_data = line.split(',')

                dict_row_data = {}
                for i in range(len(list_header)):
                    dict_row_data[ list_header[i] ] = list_row_data[i]

                list_return.append( dict_row_data )

    return list_return

def get_list_Profile_qty_price_of_this_day( this_symbol, this_day ):
    list_return = []

    file_path = './outputs/tw/' + this_symbol + '/' + 'profile_qty_price.csv'
    if not os.path.isfile(file_path):
        return []

    list_all_data = read_csv_to_dict( file_path )

    for this_row in list_all_data:
        if this_row['date'] == this_day:
            list_return.append(this_row)

    return list_return


def get_skewness_of_this_day( this_symbol, this_day):
    list_data = get_list_Profile_qty_price_of_this_day( this_symbol, this_day)
    if len(list_data) == 0:
        return [0,0,0]

    list_data = sorted( list_data, key = lambda x: float( x['price'] ) )

    list_qty_data = []
    for item in list_data:
        list_qty_data.append( float( item['qty'] ) )

    skewness_original = stats.skew( list_qty_data  )

    total_price_item_count = len(list_data)
    total_qty_this_day = sum( int(x['qty']) for x in list_data)

    # the skewness_normalize_max_qty is the same as skewness_original
    #max_qty = max(list_qty_data)
    #for i in range(len(list_qty_data)):
    #    list_qty_data[i] = list_qty_data[i] / max_qty
    #skewness_normalize_max_qty = stats.skew( list_qty_data  )

    return [skewness_original, total_price_item_count, total_qty_this_day]

def write_skewness_file_of_this_day( this_day  ):
    output_dir = './outputs/stats/skewness'
    # create full path, will judge if need to create
    os.makedirs(output_dir, exist_ok=True)

    list_symbol = get_list_symbol_from_outputs()
    list_skewness = []
    for this_symbol in list_symbol:
        list_stats = get_skewness_of_this_day(this_symbol, this_day)
        skewness = list_stats[0] 
        total_price_item_count = list_stats[1] 
        total_qty_this_day = list_stats[2]
        print( 'symbol: {} \t skewness: {:f}'.format(this_symbol, skewness) )
        
        dict_temp = {}
        dict_temp['date'] = this_day
        dict_temp['symbol'] = this_symbol
        dict_temp['skewness'] = skewness
        dict_temp['price_item_count'] = total_price_item_count
        dict_temp['total_qty'] = total_qty_this_day

        list_skewness.append(dict_temp)

    list_skewness = sorted(list_skewness, \
                    key = lambda x : ( x['price_item_count'], x['total_qty']), \
                    reverse=True)
            
    with open(output_dir + '/skewness_' + this_day + '.txt', 'w') as f:
        f.write('date,symbol,skewness,price_item_count,total_qty\n')
        
        for this_data in list_skewness:
            f.write('{},{},{:f},{},{}\n'.format( \
                        this_data['date'], \
                        this_data['symbol'], \
                        this_data['skewness'], \
                        this_data['price_item_count'], \
                        this_data['total_qty'] \
                        ))


if __name__ == '__main__':
    this_day = '20180525'
    write_skewness_file_of_this_day(this_day)
    print('\n\nDone~~\n\n')
